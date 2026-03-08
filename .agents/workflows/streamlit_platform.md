---
description: Regra para criação da plataforma Streamlit
---

## Estrutura da Plataforma
A plataforma deve conter as seguintes páginas:
- `Estatísticas Descritivas`
- `Estatísticas Preditivas`
- `Atualização de Dados`

## Estatísticas Descritivas
Deve mostrar estatísticas descritivas usando os dados importados.
- **Regra de tempo**: Os dados utilizados nos gráficos devem sempre considerar **apenas um ano** (atualmente tem os anos 2022, 2023 e 2024). A seleção de ano deve filtrar todo o dashboard.
- **Filtros Obrigatórios**:
  - Categoria Pedra
  - Fase
  - Ano corrente
  - Gênero
  - Idade
  - Escola Pública

## Gráficos Obrigatórios
- Gráficos de barras quando indicado.
- Gráfico de boxplot aplicando segregações por categoria pedra.
- Gráfico de boxplot aplicando segregações por gênero.
- Gráfico de boxplot aplicando segregações por fase.

## Separação de Arquivos
- Para **cada gráfico**, crie um arquivo `.py` específico (por exemplo, dentro de uma pasta `components/`). Esses scripts devem conter funções que geram os gráficos usando as bibliotecas adequadas (ex: `plotly` via Streamlit, ou `matplotlib`/`seaborn`), e depois são importados pelas páginas do Streamlit.

## As páginas Estatísticas Preditivas e Atualização de dados
Podem ser criadas inicialmente como páginas em branco/placeholders com os títulos adequados.

## Setup Genérico
Sempre que pertinente:
- Crie um ambiente virtual.
- Instale os pacotes necessários via `requirements.txt`.
- Ative o ambiente.
- Utilize os dados gerados pelo notebook `04_dataprep.ipynb` como origem dos dados da plataforma.
