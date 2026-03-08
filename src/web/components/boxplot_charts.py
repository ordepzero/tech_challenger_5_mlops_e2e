import plotly.express as px
import streamlit as st
import pandas as pd

def plot_boxplot(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    """Gera um gráfico boxplot genérico."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Sem dados suficientes para gerar o boxplot {title}.")
        return None

    category_orders = {}
    
    if x_col == 'Categoria Pedra':
        # Ordem fixa para as pedras
        category_orders[x_col] = ['Quartzo', 'Agata', 'Ametista', 'Topazio']
    elif x_col == 'Fase':
        # Garante ordenação sequencial se numérico ou string representacional
        fases_ordem = sorted(df[x_col].dropna().unique(), key=lambda x: str(x))
        category_orders[x_col] = fases_ordem

    fig = px.box(
        df, 
        x=x_col, 
        y=y_col, 
        color=x_col,
        category_orders=category_orders,
        title=title
    )
    
    fig.update_layout(
        xaxis_title=x_col, 
        yaxis_title=y_col, 
        showlegend=False
    )
    
    return fig
