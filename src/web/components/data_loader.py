import pandas as pd
import streamlit as st
import os
import glob

@st.cache_data
def load_data():
    data_dir = os.path.join("data", "refined")
    all_data = []
    
    file_pattern = os.path.join(data_dir, "pede_refined_*.csv")
    csv_files = glob.glob(file_pattern)
    
    for file in csv_files:
        try:
            # Extrair o ano do nome do arquivo
            filename = os.path.basename(file)
            year_str = filename.split("_")[-1].replace(".csv", "")
            year = int(year_str)
            
            df = pd.read_csv(file, sep=";")
            df['Ano corrente'] = year
            
            # Reconstruir 'Categoria Pedra'
            # As colunas originais são do tipo class_pedra_YY_pedra
            yy = str(year)[-2:]
            pedras = ['agata', 'ametista', 'quartzo', 'topazio']
            df['Categoria Pedra'] = 'N/A'
            df['Cod Categoria Pedra'] = -1
            
            for i, pedra in enumerate(pedras):
                col_name = f'class_pedra_{yy}_{pedra}'
                if col_name in df.columns:
                    mask = df[col_name] == 1
                    df.loc[mask, 'Categoria Pedra'] = pedra.capitalize()
                    df.loc[mask, 'Cod Categoria Pedra'] = i
            
            # Renomear e padronizar colunas que serão usadas como filtro
            # Fase: num_fase_atual
            # Gênero: cod_genero
            # Idade: num_idade
            # Escola Pública: is_escola_publica
            df.rename(columns={
                'num_fase_atual': 'Fase',
                'num_idade': 'Idade',
                'is_escola_publica': 'Escola Pública',
                'qtd_defasagem': 'Defasagem'
            }, inplace=True)
            # Transformar códigos em algo mais amigável, se aplicável
            df['cod_genero'] = df['cod_genero'].map({1: 1, 2: 0}).fillna(df['cod_genero'])
            df['Escola Pública'] = df['Escola Pública'].map({1: 'Sim', 0: 'Não'}).fillna(df['Escola Pública'].astype(str))
            
            all_data.append(df)
        except Exception as e:
            print(f"Erro ao ler {file}: {e}")
            
    if not all_data:
        return pd.DataFrame()
        
    df_final = pd.concat(all_data, ignore_index=True)
    return df_final
