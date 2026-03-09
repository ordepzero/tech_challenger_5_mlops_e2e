import requests
import os
import pandas as pd

API_URL = "http://localhost:8001"
PROJECT_ROOT = r'D:\arquivos_antigos\Projetos\FIAP\Fase5\tech_challenger_5_project'
data_file = os.path.join(PROJECT_ROOT, 'data', 'refined', 'pede_refined_2022.csv')

def test_models():
    print("--- Testando Modelos na API ---")
    
    # Testar se API está viva
    try:
        requests.get(API_URL)
    except:
        print(f"ERRO: API não encontrada em {API_URL}. Certifique-se de que rodou uvicorn na porta 8001.")
        return

    # Testar cada modelo
    for m_id in [1, 2, 3]:
        print(f"\n>> Testando Modelo {m_id}...")
        with open(data_file, 'rb') as f:
            files = {'file': f}
            resp = requests.post(f"{API_URL}/predict/{m_id}", files=files)
            
        if resp.status_code == 200:
            results = resp.json()
            print(f"SUCESSO! Recebi {len(results)} predições.")
            print(f"Amostra: {results[0]}")
        else:
            print(f"FALHA (Status {resp.status_code}): {resp.text}")

if __name__ == "__main__":
    test_models()
