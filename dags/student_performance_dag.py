from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import os
import pandas as pd
import sys
from pathlib import Path

# Add src to path so we can import our preprocessing logic
sys.path.append(os.path.join(os.getcwd(), 'src'))
from data_preprocessing import preprocess_data

RAW_DATA_PATH = '/opt/airflow/data/raw'
PROCESSED_DATA_PATH = '/opt/airflow/data/processed'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_new_file(**kwargs):
    # In a real scenario, we might use the filename from the sensor
    # or list files in the raw directory.
    # For this challenge, we know the file is BASE DE DADOS PEDE 2024 - DATATHON.xlsx
    file_path = os.path.join(RAW_DATA_PATH, 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    # Years to process
    years = [2022, 2023, 2024]
    sheet_names = {2022: 'PEDE2022', 2023: 'PEDE2023', 2024: 'PEDE2024'}
    
    execution_date = kwargs.get('ds') # yyyy-mm-dd
    dt_obj = datetime.strptime(execution_date, '%Y-%m-%d')
    
    for year in years:
        print(f"Processing data for year {year}...")
        df = pd.read_excel(file_path, sheet_name=sheet_names[year])
        
        # Apply preprocessing
        df_processed = preprocess_data(df, year)
        
        # Define output path with partitions
        output_dir = os.path.join(
            PROCESSED_DATA_PATH, 
            f"year={dt_obj.year}", 
            f"month={dt_obj.month:02d}", 
            f"day={dt_obj.day:02d}"
        )
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"student_performance_{year}.parquet")
        df_processed.to_parquet(output_file, index=False)
        print(f"Saved processed data to {output_file}")

with DAG(
    'student_performance_ingestion',
    default_args=default_args,
    description='Ingest and transform student performance data',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:

    wait_for_file = FileSensor(
        task_id='wait_for_new_data',
        filepath='BASE DE DADOS PEDE 2024 - DATATHON.xlsx',
        fs_conn_id='fs_default',
        poke_interval=30,
        timeout=600
    )

    transform_data = PythonOperator(
        task_id='transform_and_save_parquet',
        python_callable=process_new_file,
        provide_context=True
    )

    wait_for_file >> transform_data
