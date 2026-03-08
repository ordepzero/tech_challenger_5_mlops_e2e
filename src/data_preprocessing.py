import pandas as pd
import numpy as np
import unidecode
import unicodedata
import re
from typing import Dict, List, Optional

def rename_cols(df: pd.DataFrame, rename_dict: Dict[str, str]) -> pd.DataFrame:
    """Renames columns based on a mapping dictionary."""
    return df.rename(columns=rename_dict)

def encode_gender(df: pd.DataFrame, 
                 col_origem: str = "nome_genero", 
                 col_destino: str = "cod_genero", 
                 mapa: Optional[Dict] = None) -> pd.DataFrame:
    """Encodes gender text to numeric values."""
    if mapa is None:
        mapa = {"Menino": 0, "Masculino": 0, "Menina": 1, "Feminino": 1}
    df[col_destino] = df[col_origem].map(mapa).fillna(df[col_origem])
    return df

def calcular_fase_ingresso(df: pd.DataFrame, ano_atual_ref: int) -> pd.DataFrame:
    """Calculates age at entry and estimates entry phase."""
    if 'num_ano_ingresso' in df.columns and 'num_idade' in df.columns:
        df['idade_ingresso'] = df['num_idade'] - (ano_atual_ref - df['num_ano_ingresso'])
        
        def estimar_fase_ingresso(idade: int) -> str:
            if idade < 7: return '0'
            if 7 <= idade <= 8: return '0'
            if 8 < idade <= 9: return '1'
            if 10 <= idade <= 11: return '2'
            if 12 <= idade <= 13: return '3'
            if idade == 14: return '4'
            if idade == 15: return '5'
            if idade == 16: return '6'
            if idade == 17: return '7'
            if idade == 18: return '8'
            if idade >= 19: return '9'
            return 'Desconhecida'
        
        df['fase_ingresso_estimada'] = df['idade_ingresso'].apply(estimar_fase_ingresso)
    return df

def corrigir_idade(df: pd.DataFrame, ano_referencia: int) -> pd.DataFrame:
    """Recalculates age based on birth year."""
    df['num_ano_nascimento_dt'] = pd.to_datetime(df['num_ano_nascimento'], errors='coerce')
    # If it's already a year (int), dt.year will fail. Handle both cases.
    df['num_year_only'] = df['num_ano_nascimento_dt'].dt.year.fillna(df['num_ano_nascimento']).astype(float)
    df['num_idade'] = ano_referencia - df['num_year_only']
    df.drop(columns=['num_ano_nascimento_dt', 'num_year_only'], inplace=True, errors='ignore')
    return df

def flag_escola_publica(df: pd.DataFrame, coluna: str = 'instituicao_ensino') -> pd.DataFrame:
    """Flags if the institution is public."""
    df['is_escola_publica'] = (
        df[coluna]
        .astype(str)
        .str.lower()
        .str.contains('pública|publica')
        .astype(int)
    )
    return df

def converter_alfanumerico(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Normalizes text in specific columns."""
    def normalizar_texto(valor):
        if pd.isna(valor):
            return "ausente"
        valor = str(valor).lower()
        valor = unicodedata.normalize('NFKD', valor).encode('ASCII', 'ignore').decode('utf-8')
        valor = re.sub(r'[^a-z0-9 ]', '', valor)
        return valor.strip()

    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_texto)
    return df

def ordenar_pedras(df: pd.DataFrame, ordem_pedras: Optional[Dict] = None, cols_pedra: Optional[List[str]] = None) -> pd.DataFrame:
    """Processes stone classifications and calculates changes."""
    if ordem_pedras is None:
        ordem_pedras = {'quartzo': 1, 'agata': 2, 'ametista': 3, 'topazio': 4}
    if cols_pedra is None:
        cols_pedra = [c for c in df.columns if c.startswith("class_pedra")]
        cols_pedra = sorted(cols_pedra, key=lambda x: int(x.split("_")[-1]) if x.split("_")[-1].isdigit() else 0)
    
    df[cols_pedra] = df[cols_pedra].fillna('ausente')
    for col in cols_pedra:
        df[f'{col}_num'] = df[col].map(ordem_pedras).fillna(0).astype(int)
    
    for i in range(len(cols_pedra) - 1):
        col_atual = f"{cols_pedra[i]}_num"
        col_prox = f"{cols_pedra[i+1]}_num"
        # Try to extract year from column name like class_pedra_20
        match_atual = re.search(r'\d+', cols_pedra[i])
        match_prox = re.search(r'\d+', cols_pedra[i+1])
        if match_atual and match_prox:
            ano_atual = match_atual.group()
            ano_prox = match_prox.group()
            df[f"mudanca_class_pedra_{ano_atual}_{ano_prox}"] = (df[col_prox] - df[col_atual]).astype(int)
    
    df.drop(columns=[f"{c}_num" for c in cols_pedra], inplace=True)
    return df

def calcular_avaliacoes(df: pd.DataFrame, mapa_avaliacao: Optional[Dict] = None) -> pd.DataFrame:
    """Calculates min/max scores for evaluators."""
    if mapa_avaliacao is None:
        mapa_avaliacao = {
            'Alocado em Fase anterior': 0,
            'Não avaliado': 1,
            'Mantido na Fase atual': 2,
            'Mantido na Fase + Bolsa': 3,
            'Promovido de Fase': 4,
            'Promovido de Fase + Bolsa': 5
        }
    cols_avaliadores = [c for c in df.columns if 'observ_avaliador_' in c]
    if cols_avaliadores:
        df[cols_avaliadores] = df[cols_avaliadores].fillna('Não avaliado')
        df_aval_num = df[cols_avaliadores].replace(mapa_avaliacao)
        # Handle cases where some values might not be in map
        df_aval_num = df_aval_num.apply(pd.to_numeric, errors='coerce').fillna(1).astype(int)
        df['melhor_avaliacao_score'] = df_aval_num.max(axis=1)
        df['pior_avaliacao_score'] = df_aval_num.min(axis=1)
    return df

def extrair_flags_texto(df: pd.DataFrame, cols_texto_obs: Optional[List[str]] = None) -> pd.DataFrame:
    """Extracts 'Destaque' and 'Melhorar' flags from text observations."""
    if cols_texto_obs is None:
        cols_texto_obs = ['observ_engajamento', 'observ_aprendizagem', 'observ_ponto_virada']
    for col in cols_texto_obs:
        if col in df.columns:
            df[f'{col}_tem_destaque'] = df[col].astype(str).str.contains('Destaque', case=False, na=False).astype(int)
            df[f'{col}_tem_melhorar'] = df[col].astype(str).str.contains('Melhorar', case=False, na=False).astype(int)
    return df

def flag_atencao_psicologica(df: pd.DataFrame, coluna: str = 'observ_psico') -> pd.DataFrame:
    """Flags students needing psychological attention."""
    if coluna in df.columns:
        valores_atencao = ['Requer avaliação', 'Não indicado']
        df['flag_observ_psico'] = df[coluna].isin(valores_atencao).astype(int)
    return df

def criar_flags_defasagem(df: pd.DataFrame, col_defasagem: str = 'qtd_defasagem') -> pd.DataFrame:
    """Flags positive/negative school delay."""
    if col_defasagem in df.columns:
        df['defasagem_positiva'] = df[col_defasagem].apply(lambda x: 1 if x > 0 else 0)
        df['defasagem_negativa'] = df[col_defasagem].apply(lambda x: 1 if x < 0 else 0)
    return df

def padronizar_fase(df: pd.DataFrame, col_fase: str = "nome_fase") -> pd.DataFrame:
    """Standardizes phase names/numbers."""
    def converter_fase(valor):
        if pd.isna(valor): return None
        valor_str = str(valor).strip().upper()
        if valor_str == "ALFA": return 0
        if valor_str.startswith("FASE"):
            try: return int(valor_str.replace("FASE", "").strip())
            except: return None
        match = re.match(r"^(\d+)", valor_str)
        if match: return int(match.group(1))
        try: return int(valor_str)
        except: return None
    df["num_fase_atual"] = df[col_fase].apply(converter_fase)
    return df

def criar_flag_bolsa(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Flags if student has a scholarship."""
    if col not in df.columns: return df
    serie = df[col].fillna("").astype(str).str.lower()
    if "bolsa" in col.lower() or col == "flag_indicado_bolsa":
        df["flag_bolsa_estudos"] = serie.apply(lambda x: 1 if "sim" in x else 0)
    elif col == "instituicao_ensino":
        palavras_bolsa = ["bolsa", "apadrinhamento", "parceria", "parceira"]
        df["flag_bolsa_estudos"] = serie.apply(lambda x: 1 if any(p in x for p in palavras_bolsa) else 0)
    return df

# Mappings for each year extracted from notebooks
MAPPINGS = {
    2022: {
        "RA": "registro_unico", "Fase": "nome_fase", "Turma": "nome_turma", "Ano nasc": "num_ano_nascimento",
        "Nome": "nome_anonimizado", "Idade 22": "num_idade", "Gênero": "nome_genero", "Ano ingresso": "num_ano_ingresso",
        "Instituição de ensino": "instituicao_ensino", "Pedra 20": "class_pedra_20", "Pedra 21": "class_pedra_21",
        "Pedra 22": "class_pedra_22", "INDE 22": "indic_desenv_educ_22", "Cg": "class_geral", "Cf": "class_fase",
        "Ct": "class_turma", "Nº Av": "num_avaliacao", "Avaliador1": "nome_avaliador_1", "Rec Av1": "observ_avaliador_1",
        "Avaliador2": "nome_avaliador_2", "Rec Av2": "observ_avaliador_2", "Avaliador3": "nome_avaliador_3", "Rec Av3": "observ_avaliador_3",
        "Avaliador4": "nome_avaliador_4", "Rec Av4": "observ_avaliador_4", "IAA": "indic_auto_avaliacao", "IEG": "indic_engajamento",
        "IPS": "indic_psicossocial", "Rec Psicologia": "observ_psico", "IDA": "indic_aprendizagem", "Matem": "nota_media_matematica",
        "Portug": "nota_media_portugues", "Inglês": "nota_media_ingles", "Indicado": "flag_indicado_bolsa", "Atingiu PV": "flag_atingiu_ponto_virada",
        "IPV": "nota_media_ponto_virada", "IAN": "nota_media_adequacao", "Fase ideal": "fase_nome_ideal", "Defas": "qtd_defasagem",
        "Destaque IEG": "observ_engajamento", "Destaque IDA": "observ_aprendizagem", "Destaque IPV": "observ_ponto_virada"
    },
    2023: {
        "RA": "registro_unico", "Fase": "nome_fase", "Turma": "nome_turma", "Data de Nasc": "num_ano_nascimento",
        "Nome Anonimizado": "nome_anonimizado", "Idade": "num_idade", "Gênero": "nome_genero", "Ano ingresso": "num_ano_ingresso",
        "Instituição de ensino": "instituicao_ensino", "Pedra 20": "class_pedra_20", "Pedra 21": "class_pedra_21",
        "Pedra 22": "class_pedra_22", "INDE 22": "indic_desenv_educ_22", "Pedra 2023": "class_pedra_23", "INDE 2023": "indic_desenv_educ_23",
        "Cg": "class_geral", "Cf": "class_fase", "Ct": "class_turma", "Nº Av": "num_avaliacao", "Avaliador1": "nome_avaliador_1",
        "Rec Av1": "observ_avaliador_1", "Avaliador2": "nome_avaliador_2", "Rec Av2": "observ_avaliador_2", "Avaliador3": "nome_avaliador_3",
        "Rec Av3": "observ_avaliador_3", "Avaliador4": "nome_avaliador_4", "Rec Av4": "observ_avaliador_4", "IAA": "indic_auto_avaliacao",
        "IEG": "indic_engajamento", "IPS": "indic_psicossocial", "Rec Psicologia": "observ_psico", "IDA": "indic_aprendizagem",
        "Mat": "nota_media_matematica", "Por": "nota_media_portugues", "Ing": "nota_media_ingles", "Indicado": "flag_indicado_bolsa",
        "Atingiu PV": "flag_atingiu_ponto_virada", "IPV": "nota_media_ponto_virada", "IAN": "nota_media_adequacao", "Fase Ideal": "fase_nome_ideal",
        "Defasagem": "qtd_defasagem", "Destaque IEG": "observ_engajamento", "Destaque IDA": "observ_aprendizagem", "Destaque IPV": "observ_ponto_virada"
    },
    2024: {
        "RA": "registro_unico", "Fase": "nome_fase", "Turma": "nome_turma", "Data de Nasc": "num_ano_nascimento",
        "Nome Anonimizado": "nome_anonimizado", "Idade": "num_idade", "Gênero": "nome_genero", "Ano ingresso": "num_ano_ingresso",
        "Instituição de ensino": "instituicao_ensino", "Pedra 20": "class_pedra_20", "Pedra 21": "class_pedra_21",
        "Pedra 22": "class_pedra_22", "Pedra 23": "class_pedra_23", "Pedra 2024": "class_pedra_24", "INDE 22": "indic_desenv_educ_22",
        "INDE 23": "indic_desenv_educ_23", "INDE 2024": "indic_desenv_educ_24", "Cg": "class_geral", "Cf": "class_fase",
        "Ct": "class_turma", "Nº Av": "num_avaliacao", "Avaliador1": "nome_avaliador_1", "Rec Av1": "observ_avaliador_1",
        "Avaliador2": "nome_avaliador_2", "Rec Av2": "observ_avaliador_2", "Avaliador3": "nome_avaliador_3", "Avaliador4": "nome_avaliador_4",
        "Avaliador5": "Avaliador5", "Avaliador6": "Avaliador6", "IAA": "indic_auto_avaliacao", "IEG": "indic_engajamento",
        "IPS": "indic_psicossocial", "Rec Psicologia": "observ_psico", "IDA": "indic_aprendizagem", "Mat": "nota_media_matematica",
        "Por": "nota_media_portugues", "Ing": "nota_media_ingles", "Indicado": "flag_indicado_bolsa", "Atingiu PV": "flag_atingiu_ponto_virada",
        "IPV": "nota_media_ponto_virada", "IAN": "nota_media_adequacao", "Fase Ideal": "fase_nome_ideal", "Defasagem": "qtd_defasagem",
        "Destaque IEG": "observ_engajamento", "Destaque IDA": "observ_aprendizagem", "Destaque IPV": "observ_ponto_virada"
    }
}

def preprocess_data(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Main function to apply all preprocessing steps dynamically based on the year."""
    if year not in MAPPINGS:
        raise ValueError(f"Mappings for year {year} not found.")
    
    # 1. Rename columns
    df = rename_cols(df, MAPPINGS[year])
    
    # 2. Basic cleanup
    df['num_ano_nascimento'] = df['num_ano_nascimento'].fillna(0) # Temporary fix
    df = corrigir_idade(df, year)
    df = encode_gender(df)
    df = calcular_fase_ingresso(df, year)
    df = flag_escola_publica(df)
    
    # 3. Categorical normalization
    df = converter_alfanumerico(df, [c for c in df.columns if "class_pedra" in c])
    df = ordenar_pedras(df)
    
    # 4. Evaluation scores
    df = calcular_avaliacoes(df)
    df = extrair_flags_texto(df)
    df = flag_atencao_psicologica(df)
    
    # 5. Delay and Phase
    df = criar_flags_defasagem(df)
    df = padronizar_fase(df)
    
    # 6. Scholarship
    if "flag_indicado_bolsa" in df.columns:
        df = criar_flag_bolsa(df, "flag_indicado_bolsa")
    else:
        df = criar_flag_bolsa(df, "instituicao_ensino")
    
    # 7. Timestamps for Feast
    df['event_timestamp'] = pd.to_datetime(f"{year}-01-01")
    df['created_timestamp'] = pd.Timestamp.now()
        
    return df
