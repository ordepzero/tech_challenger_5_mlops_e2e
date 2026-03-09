# Datathon: Previsão de Defasagem Escolar - Passos Mágicos

<p align="center">
  <img src="https://passosmagicos.org.br/wp-content/themes/passos-magicos/assets/images/logo.png" alt="Passos Mágicos Logo" width="200"/>
</p>

## Sobre a Passos Mágicos

A **Passos Mágicos** é uma associação sem fins lucrativos que atua na transformação da vida de crianças e jovens de baixa renda, proporcionando melhores oportunidades através de educação de qualidade, auxílio psicológico/psicopedagógico e ampliação da visão de mundo. 

Saiba mais em: [passosmagicos.org.br](https://passosmagicos.org.br/)

## O Desafio (Tech Challenger 5 - FIAP)

Este projeto faz parte do **Tech Challenger 5** do curso de Pós-Graduação em Engenharia de Machine Learning da **FIAP**. O objetivo central é desenvolver modelos de Machine Learning capazes de estimar o **risco de defasagem escolar** de cada estudante atendido pela associação nos ciclos de 2022, 2023 e 2024.

O sistema visa atuar como uma ferramenta de apoio à decisão, permitindo que a coordenação pedagógica identifique precocemente alunos em situação crítica e direcione recursos de forma mais assertiva.

---

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         src and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## Tratamento de Dados e Justificativas (EDA & DataPrep)

Antes da modelagem, os dados passaram por um rigoroso processo de limpeza e padronização, detalhado nos notebooks `01` a `04`. Abaixo estão os principais tratamentos e suas motivações técnicas:

### 1. Padronização de Esquemas (Multi-ano)
*   **Ação:** Renomeação de colunas variadas (ex: `RA`, `Nome Anonimizado`, `Idade 22`) para um padrão único (`registro_unico`, `nome_anonimizado`, `num_idade`).
*   **Justificativa:** Os nomes das colunas mudavam a cada ano da base PEDE. A padronização é essencial para permitir o *join* temporal via Feast e o treinamento de modelos em bases unificadas.

### 2. Saneamento de Idades e Datas
*   **Ação:** Recálculo da idade com base no `num_ano_nascimento` e um ano de referência fixo.
*   **Justificativa:** Identificamos inconsistências onde o campo "Idade" não batia com o ano de nascimento em alguns registros. O recálculo garante que a "idade" seja uma feature comparável entre diferentes safras de dados.

### 3. Codificação de Gênero e Instituição
*   **Ação:** Mapeamento de `Menino/Masculino` para `0` e `Menina/Feminino` para `1`. Identificação binária de Escola Pública.
*   **Justificativa:** Modelos de Machine Learning exigem entradas numéricas. A unificação de termos (Menino vs Masculino) remove ruídos de digitação.

### 4. Tratamento de "Pedras" (Classificação Passos Mágicos)
*   **Ação:** Normalização de strings (remoção de acentos), tratamento de valores ausentes como "quartzo" (ou categoria base) e criação de variáveis de "Mudança de Pedra" entre anos.
*   **Justificativa:** A "Pedra" é o principal indicador de progresso. Criar uma feature de "evolução" (subiu ou desceu de pedra) permite que o modelo capture a trajetória do aluno, não apenas seu estado atual.

### 5. Engenharia de Features de Texto (NLP Básico)
*   **Ação:** Extração de flags binárias (`tem_destaque`, `tem_melhorar`) a partir dos campos de observações dos avaliadores.
*   **Justificativa:** Transformamos feedbacks qualitativos subjetivos em indicadores quantitativos que sinalizam proatividade ou necessidade de atenção imediata.

### 6. Tratamento de Missing Values (Imputação)
*   **Ação:** Notas ausentes foram tratadas dependendo do contexto (em alguns casos preenchidas com a média da fase, em outros mantidas como sinalizadores de novos alunos).
*   **Justificativa:** Evita o descarte de registros valiosos (especialmente de alunos novos) e mantém a integridade estatística das variáveis de desempenho (IDA, IEG, etc).

--------


## Modelagem e Justificativas

No projeto da Passos Mágicos, exploramos três abordagens principais para prever o desempenho e o risco dos alunos, utilizando modelos de Machine Learning rastreados pelo MLflow.

### Modelos Utilizados

1.  **Random Forest (Floresta Aleatória):**
    *   **Por que usar?** É um modelo robusto que lida bem com relações não-lineares entre as características do aluno (como idade, gênero e notas). Além disso, ele é menos propenso a overfitting do que uma única árvore de decisão e fornece a "importância das features", o que nos ajuda a entender quais fatores mais influenciam o sucesso do aluno.
    *   **Aplicação:** Utilizado nas Abordagens 1 e 2 para capturar a complexidade dos dados históricos.

2.  **Logistic Regression (Regressão Logística):**
    *   **Por que usar?** É o modelo padrão para classificações binárias (ex: Risco vs. Não Risco). É extremamente interpretável, permitindo ver exatamente como cada variável aumenta ou diminui a probabilidade do evento. Serve como um excelente *baseline* para comparar com modelos mais complexos.
    *   **Aplicação:** Utilizado na Abordagem 3 para prever o risco global de defasagem na base unificada.

### Estratégias de Treinamento

*   **Abordagem 1 (Snapshot 2022):** Focada em prever se o aluno apresenta **defasagem** em 2022 usando apenas dados desse ano. É a forma mais direta de identificar riscos educacionais imediatos sem depender de histórico externo ao ciclo atual.
*   **Abordagem 2 (Expansão de Contexto):** Incorpora indicadores de evasão (saída em 2023) e defasagem negativa, enriquecendo o perfil do aluno para uma predição mais sensível a riscos sociais.
*   **Abordagem 3 (Base Unificada):** Combina todos os anos (2022-2024) em um único dataset para aumentar o volume de dados e permitir que o modelo aprenda padrões gerais que persistem ao longo do tempo.

### Métricas de Avaliação e Confiabilidade

A escolha das métricas visa garantir que o modelo seja **confiável para entrar em produção**:

*   **Acurácia (Accuracy):** Indica a proporção total de acertos. Se o valor for **X**, o modelo acertou **X%** das situações gerais. Entretanto, em bases desbalanceadas, ela pode ser enganosa.
*   **F1-Score (Macro):** É a nossa métrica de controle. Um valor **Y** indica o equilíbrio entre precisão e recall para todas as classes. 

### Fluxo de Dados da plataforma

A plataforma segue um ciclo de vida de dados estruturado para garantir que as predições sejam consistentes e baseadas em dados validados:

1.  **Carga (Upload):** O usuário fornece um arquivo (CSV/Excel) via interface Streamlit.
2.  **Validação:** O sistema verifica se as colunas essenciais (ex: `registro_unico`, `num_idade`) estão presentes e se os valores respeitam o domínio esperado (ex: idades positivas, flags binárias).
3.  **Enriquecimento (Feature Store):**
    *   **Offline Store (Parquet):** Os dados históricos consolidados (2022-2024) são usados para treinar o modelo e realizar backtesting de longo prazo.
    *   **Online Store (SQLite):** Utilizado para prover as features mais recentes com baixa latência durante a inferência na plataforma.
4.  **Predição:** O modelo carrega os pesos (via MLflow) e gera o resultado.
5.  **Persistência:** Importante notar que os dados carregados para predição são **temporários** (em memória). A base oficial `all.parquet` só é atualizada via notebook de Feature Store para garantir governança.

**Por que o Feast serve de duas formas?**
*   **Offline:** Essencial para "Point-in-Time Joins". Ele reconstrói o passado exatamente como ele era no momento de cada evento, evitando vazamento de dados (*data leakage*).
*   **Online:** Otimizado para consultas rápidas de um único `registro_unico`. Em vez de ler um arquivo Parquet de 3000 linhas, ele acessa um índice SQLite de alta performance.

### Análise de Confiabilidade:
- **Abordagens 1 e 2:** Apresentam métricas de Acurácia e F1-Score muito próximas. Isso indica que os modelos são equilibrados e altamente confiáveis para prever tanto a classe majoritária quanto os casos críticos.
- **Abordagem 3:** Pode apresentar uma lacuna entre Acurácia (alta) e F1-Score (baixo). Isso indica desbalanceamento de classes, onde o modelo prioriza a classe mais frequente. Para produção, isso requer técnicas de balanceamento (como SMOTE ou pesos de classe) para evitar falsos negativos em alunos de risco.

### Resultados Obtidos

As três abordagens foram testadas utilizando `Random Forest` e `Logistic Regression` (Abordagem 3), com os seguintes resultados preliminares:

| Abordagem | Modelo | Acurácia | F1-Score (Macro) | Contexto |
| :--- | :--- | :--- | :--- | :--- |
| **Modelo 1** | Random Forest | ~92.5% | ~0.89 | Previsão de Defasagem em 2022 |
| **Modelo 2** | Random Forest | ~88.3% | ~0.85 | Join 2022+2023 via registro_unico |
| **Modelo 3** | Logistic Regression | ~85.6% | ~0.82 | Base unificada 2022-2024 via Feature Store |

> [!NOTE]
> A Abordagem 1 apresenta a maior acurácia por lidar com um subconjunto mais específico de alunos veteranos, enquanto a Abordagem 3 foca na generalização através de todo o histórico via Feature Store.

---

## 🚀 Como Executar o Projeto

1. Crie o ambiente virtual e instale os pacotes de `requirements.txt`
2. Processe os dados base: `.\.venv\Scripts\python -m jupyter nbconvert --execute notebooks/04_dataprep.ipynb --to notebook --inplace`
3. Configure a Feature Store: `.\.venv\Scripts\python -m jupyter nbconvert --execute notebooks/05_feature_store.ipynb --to notebook --inplace`
4. Execute o treinamento e comparação: `.\.venv\Scripts\python -m jupyter nbconvert --execute notebooks/06_model.ipynb --to notebook --inplace`
5. **Inicie a API de Predição (Necessário para o Dashboard):** 
   ```powershell
   .\.venv\Scripts\python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001
   ```
6. Inicie o dashboard Streamlit: `.\.venv\Scripts\python -m streamlit run src/web/app.py`

### 🛠️ Exploração de Infraestrutura

*   **Feast UI:** Para visualizar as entidades, features e o estado do repositório, execute:
    ```powershell
    cd feature_repo
    ..\.venv\Scripts\feast ui
    ```
    Acesse em `http://localhost:8888`.
*   **MLflow UI:** Para comparar experimentos e versões de modelos:
    ```powershell
    .\.venv\Scripts\mlflow ui --backend-store-uri sqlite:///mlflow.db
    ```
    Acesse em `http://localhost:5000`.