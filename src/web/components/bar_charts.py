import plotly.express as px
import streamlit as st
import pandas as pd
from typing import Optional

def plot_bar_chart(df: pd.DataFrame, x_col: str, title: str, color_col: Optional[str] = None):
    """Gera um gráfico de barras dadas as colunas x e o DataFrame filtrado, com cor opcional."""
    if df.empty:
        st.warning("Sem dados suficientes para gerar o gráfico.")
        return None

    if color_col:
        counts = df.groupby([x_col, color_col]).size().reset_index(name='Quantidade')
        
        # Garantir domínios discretos convertendo para string
        counts[x_col] = counts[x_col].astype(str)
        counts[color_col] = counts[color_col].astype(str)
        
        # Mapeamento de Gênero
        genero_map = {'0': 'Masculino', '1': 'Feminino', '0.0': 'Masculino', '1.0': 'Feminino'}
        if x_col == 'cod_genero':
            counts[x_col] = counts[x_col].map(genero_map).fillna(counts[x_col])
        if color_col == 'cod_genero':
            counts[color_col] = counts[color_col].map(genero_map).fillna(counts[color_col])
        
        # Garantir a ordenação
        category_orders = {}
        if x_col == 'Fase':
             category_orders[x_col] = sorted(counts[x_col].dropna().unique(), key=lambda x: int(float(x)) if str(x).replace('.','',1).isdigit() else str(x))
             
        if color_col == 'Categoria Pedra':
             category_orders[color_col] = ['Quartzo', 'Agata', 'Ametista', 'Topazio']
        elif color_col == 'Fase':
             category_orders[color_col] = sorted(counts[color_col].dropna().unique(), key=lambda x: int(float(x)) if str(x).replace('.','',1).isdigit() else str(x))
             
        fig = px.bar(
            counts, 
            x=x_col, 
            y='Quantidade',
            color=color_col,
            title=title,
            text_auto=True,
            category_orders=category_orders,
            barmode='group'
        )
    else:
        counts = df[x_col].value_counts().reset_index()
        counts.columns = [x_col, 'Quantidade']
        
        # Garantir domínios discretos
        counts[x_col] = counts[x_col].astype(str)
        
        # Mapeamento de Gênero
        genero_map = {'0': 'Masculino', '1': 'Feminino', '0.0': 'Masculino', '1.0': 'Feminino'}
        if x_col == 'cod_genero':
            counts[x_col] = counts[x_col].map(genero_map).fillna(counts[x_col])

        category_orders = {}
        if x_col == 'Fase':
             category_orders[x_col] = sorted(counts[x_col].dropna().unique(), key=lambda x: int(float(x)) if str(x).replace('.','',1).isdigit() else str(x))

        fig = px.bar(
            counts, 
            x=x_col, 
            y='Quantidade',
            title=title,
            color=x_col,
            category_orders=category_orders,
            text_auto=True
        )

    fig.update_layout(xaxis_title=x_col, yaxis_title="Quantidade")
    return fig
