import streamlit as st
from components.data_loader import load_data
from components.bar_charts import plot_bar_chart
from components.boxplot_charts import plot_boxplot

st.title("Estatísticas Descritivas")

# 1. Carregar Dados
df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado. Por favor, execute o notebook de preparação.")
    st.stop()

st.sidebar.header("Filtros")

# Filtro Ano Corrente (sempre apenas um ano por vez)
anos_disponiveis = sorted(df['Ano corrente'].unique().tolist(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Ano corrente", anos_disponiveis)

# Filtrar base primeiro pelo ano
df_filtrado = df[df['Ano corrente'] == ano_selecionado].copy()

# Outros Filtros dinâmicos baseados no ano selecionado
with st.sidebar.expander("Filtros Adicionais", expanded=True):
    # Categoria Pedra
    categorias_pedra = ["Todas"] + ['Quartzo', 'Agata', 'Ametista', 'Topazio']
    categoria_selecionada = st.selectbox("Categoria Pedra", categorias_pedra)

    # Fase
    fases_disponiveis = ["Todas"] + sorted(df_filtrado['Fase'].dropna().unique().tolist(), key=lambda x: str(x))
    fase_selecionada = st.selectbox("Fase", fases_disponiveis)

    # Gênero
    generos_disponiveis = ["Todos"] + sorted(df_filtrado['cod_genero'].unique().tolist())
    genero_selecionado = st.selectbox("Gênero", generos_disponiveis)

    # Escola Pública
    escolas_disponiveis = ["Todas"] + sorted(df_filtrado['Escola Pública'].unique().tolist())
    escola_selecionada = st.selectbox("Escola Pública", escolas_disponiveis)

    # Idade (Min e Max baseado no dataset)
    min_idade = int(df_filtrado['Idade'].min())
    max_idade = int(df_filtrado['Idade'].max())
    idade_selecionada = st.slider("Idade", min_idade, max_idade, (min_idade, max_idade))

# Aplicar filtros adicionais
if categoria_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoria Pedra'] == categoria_selecionada]
if fase_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Fase'] == fase_selecionada]
if genero_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['cod_genero'] == genero_selecionado]
if escola_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Escola Pública'] == escola_selecionada]

df_filtrado = df_filtrado[
    (df_filtrado['Idade'] >= idade_selecionada[0]) & 
    (df_filtrado['Idade'] <= idade_selecionada[1])
]

st.markdown(f"**Total de registros filtrados para {ano_selecionado}:** {len(df_filtrado)}")

# Layout de gráficos
if len(df_filtrado) == 0:
    st.info("Nenhum dado encontrado para os filtros selecionados.")
else:
    st.subheader("Distribuição Geral")
    
    segregracao_opcao = st.radio(
        "Segregar barras por:", 
        options=["Nenhuma", "Categoria Pedra", "Defasagem"],
        horizontal=True
    )
    
    if segregracao_opcao == "Categoria Pedra":
        color_param = "Categoria Pedra"
    elif segregracao_opcao == "Defasagem":
        color_param = "Defasagem"
    else:
        color_param = None

    # Filtros e ordenacao estao nos componentes/dados, os graficos de barra usam count interno
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_bar_chart(df_filtrado, 'Fase', 'Quantidade por Fase', color_col=color_param), use_container_width=True)
    with col2:
        st.plotly_chart(plot_bar_chart(df_filtrado, 'cod_genero', 'Quantidade por Gênero', color_col=color_param), use_container_width=True)
        
    col1_bot, col2_bot = st.columns(2)
    with col1_bot:
        st.plotly_chart(plot_bar_chart(df_filtrado, 'Escola Pública', 'Quantidade por Escola Pública', color_col=color_param), use_container_width=True)
    with col2_bot:
        defasagem_color = color_param if color_param != "Defasagem" else None
        st.plotly_chart(plot_bar_chart(df_filtrado, 'Defasagem', 'Quantidade por Defasagem', color_col=defasagem_color), use_container_width=True)

    st.markdown("---")
    st.subheader("Análise de Idade")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(plot_boxplot(df_filtrado, 'Fase', 'Idade', 'Idade x Fase'), use_container_width=True)
    with col4:
        pass

    st.markdown("---")
    st.subheader("Indicadores de Desempenho (Média das Notas x Categoria Pedra)")
    
    # Filtro específico para as notas
    st.markdown("Selecione uma fase específica para visualizar as notas:")
    # Reusa a lista de fases reais presentes no df base do ano correspondente, tira o 'Todas'
    fases_notas = sorted(df[df['Ano corrente'] == ano_selecionado]['Fase'].dropna().unique().tolist(), key=lambda x: str(x))
    
    if not fases_notas:
        st.info("Nenhum dado de fase disponível para exibir as notas.")
    else:
        # Se a fase_selecionada no sidebar nao for "Todas", usar ela como default, senão a primeira
        default_fase_index = fases_notas.index(fase_selecionada) if fase_selecionada != "Todas" and fase_selecionada in fases_notas else 0
        fase_notas_selecionada = st.selectbox("Fase para Notas", fases_notas, index=default_fase_index)
        
        df_notas = df_filtrado[df_filtrado['Fase'] == fase_notas_selecionada]
        
        if len(df_notas) == 0:
            st.info(f"Nenhum dado encontrado para a Fase {fase_notas_selecionada} com os filtros atuais.")
        else:
            col5, col6, col7 = st.columns(3)
            with col5:
                if 'nota_media_matematica' in df_notas.columns:
                    st.plotly_chart(plot_boxplot(df_notas, 'Categoria Pedra', 'nota_media_matematica', f'Matemática - Fase {fase_notas_selecionada}'), use_container_width=True)
                else:
                    st.warning('nota_media_matematica não disponível')
            with col6:
                if 'nota_media_portugues' in df_notas.columns:
                    st.plotly_chart(plot_boxplot(df_notas, 'Categoria Pedra', 'nota_media_portugues', f'Português - Fase {fase_notas_selecionada}'), use_container_width=True)
                else:
                    st.warning('nota_media_portugues não disponível')
            with col7:
                if 'nota_media_ingles' in df_notas.columns:
                    st.plotly_chart(plot_boxplot(df_notas, 'Categoria Pedra', 'nota_media_ingles', f'Inglês - Fase {fase_notas_selecionada}'), use_container_width=True)
                else:
                    st.warning('nota_media_ingles não disponível')
