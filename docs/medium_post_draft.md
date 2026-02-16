# Deploy de APIs no Google Cloud Run via GitHub Actions

Colocar uma API em produção exige mais do que apenas escrever o código. É necessário pensar em escalabilidade, segurança e automação. Neste artigo, vou mostrar o passo a passo de como estruturamos o deploy automatizado (CI/CD) de uma API no **Google Cloud Platform (GCP)** utilizando **Cloud Run**, **Artifact Registry** e garantindo a segurança com **Workload Identity Federation**. Ao final deste artigo você será capaz de disponibilizar um serviço via API hospedada na nuvem da Google.

## Visão Geral da Solução

Nossa jornada foca em transformar o desenvolvimento local em uma API resiliente e pronta para a nuvem. O objetivo é empacotar a aplicação em um **Container Docker**, armazená-lo em um repositório seguro no GCP e disparar o deploy automaticamente toda vez que houver uma atualização no seu repositório no GitHub.

### Tecnologias Utilizadas:
- **FastAPI:** Framework moderno e de alto desempenho para construir APIs.
- **Docker:** Para garantir consistência entre os ambientes de desenvolvimento e produção.
- **GitHub Actions:** Orquestração do pipeline de CI/CD.
- **Google Cloud Run:** Hospedagem serverless, escalável e econômica.
- **Workload Identity Federation (WIF):** Autenticação moderna e segura entre GitHub e Google Cloud.

---

## Por que escolhemos o Cloud Run?

Antes do passo a passo, vale destacar por que o Cloud Run é o favorito para este tipo de solução:
- **Serverless (Sem Servidor):** Você não gerencia máquinas. Só sobe o container e o Google cuida do resto.
- **Auto-escalonamento:** Se a API receber 1 ou 1.000 requisições, ele escala automaticamente.
- **Custo-benefício (Pay-per-use):** Você só paga quando a API está processando algo. Zero requisições = Zero custo.
- **HTTPS Nativo:** Ele já te entrega uma URL segura pronta para uso.

---

## Pré-requisitos e Preparação

Você precisará do **Google Cloud SDK** instalado localmente.
- [Instalação do Cloud SDK](https://cloud.google.com/sdk/docs/install)
> **Nota:** Não vamos nos aprofundar na instalação do SDK aqui, ele é apenas nossa ferramenta para gerenciar a nuvem via terminal.

---

## 1. Estrutura do Projeto

Para esta demonstração, utilizaremos uma estrutura simplificada, ideal para entender o fluxo de CI/CD sem se perder em subpastas complexas:

```text
.
├── .github/
│   └── workflows/
│       └── cloud_run_docker.yaml  # Nosso pipeline de CI/CD
├── models/
│   └── model.pkl                # Onde ficam seus binários de ML
├── src/
│   └── app/
│       └── main.py              # Código da API FastAPI
├── Dockerfile                   # Instruções do Container
├── requirements.txt             # Dependências Python
└── ...
```

### O que colocar em cada arquivo?

**`requirements.txt` (Minimalista):**
```text
fastapi
uvicorn
# Adicione pandas ou scikit-learn se seu modelo precisar
```

**`src/app/main.py` (Base da API):**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "service": "ML API"}

@app.get("/predict")
def predict(data: dict):
    # Lógica de predição aqui
    return {"prediction": "input_processed"}
```

**`Dockerfile` (O coração do container):**
Não vamos nos aprofundar em todos os conceitos de Docker, mas o essencial que você precisa saber é que este arquivo define "a receita" da sua imagem. Ele diz qual versão do Python usar, quais arquivos copiar e como iniciar sua API.

```dockerfile
# Imagem base leve com Python 3.12
FROM python:3.12-slim

WORKDIR /app

# Copia e instala as dependências primeiro (otimiza o cache do Docker)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código e os modelos
COPY ./src /app/src
COPY ./models /app/models

# Comando para iniciar o servidor FastAPI usando Uvicorn
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 2. Configurando o Google Cloud (GCP)

### Criando e Ativando o Projeto
```bash
# 1. Cria o projeto (ID deve ser único no mundo)
gcloud projects create meu-id-unico-mlops --name="MLOps Project"

# 2. Ativa o projeto localmente
gcloud config set project meu-id-unico-mlops
```

### Ativando APIs e Criando o Registry
```bash
# Habilita as APIs de Cloud Run, Registry e Identidade
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    iamcredentials.googleapis.com

# Cria o repósitório de imagens
gcloud artifacts repositories create ml-api-repo \
    --repository-format=docker \
    --location=us-central1
```

**Verificação:**
- **Console:** Vá em **Artifact Registry**. Seu repositório deve estar lá.
- **CLI:** Rode `gcloud artifacts repositories list`.

---

## 3. Identidades e Permissões (IAM)

### Criando a Service Account
```bash
gcloud iam service accounts create cloud-run-deployer --display-name="GitHub Deployer"
```

**Verificação:**
- **Console:** Em **IAM e Administrador > Contas de Serviço**.
- **CLI:** `gcloud iam service accounts list`.

### Atribuindo as Roles cruciais
A conta precisa dessas permissões no projeto:
- `roles/run.admin` (Admin do Cloud Run)
- `roles/artifactregistry.admin` (Admin do Registry)
- `roles/iam.serviceAccountUser` (Para usar a conta de runtime)

---

## 4. Configurando a Confiança (IAM Binding)

Agora vem o passo mais importante: permitir que o Pool de Identidade que você criou no GCP "fale" com a sua Service Account quando o request vier do repositório correto.

1. **O conceito de "principalSet":**
   Este é o valor que identifica seu repositório dentro do Pool. Ele segue o formato:
   `principalSet://iam.googleapis.com/projects/[PROJECT_NUMBER]/locations/global/workloadIdentityPools/ml-api-pool/attribute.repository/[GITHUB_ORG/REPO]`

2. **O comando de união:**
   Execute o comando abaixo para autorizar o GitHub a usar a Service Account:
   ```bash
   gcloud iam service accounts add-iam-policy-binding "cloud-run-deployer@[PROJECT_ID].iam.gserviceaccount.com" \
       --project="[PROJECT_ID]" \
       --role="roles/iam.workloadIdentityUser" \
       --member="principalSet://iam.googleapis.com/projects/[PROJECT_NUMBER]/locations/global/workloadIdentityPools/ml-api-pool/attribute.repository/[GITHUB_ORG/REPO]"
   ```
   > **O que isso faz?** Ele diz ao GCP: "Se um token vier deste repositório específico e passar pelo `ml-api-pool`, ele tem permissão para agir como o `cloud-run-deployer`".

### Dados Importantes:
- **Project Number:** Veja no Dashboard do Console ou com `gcloud projects describe [PROJECT_ID] --format="value(projectNumber)"`.
- **GitHub Repos:** Nome no formato `usuario/projeto`.

---

## 5. O Pipeline no GitHub Actions

Utilizaremos o mesmo script que usamos no projeto, garantindo compatibilidade total:

```yaml
name: Build and Deploy to Cloud Run

on:
  push:
    branches: [ "main" ]

env:
  PROJECT_ID: ${{ secrets.RUN_PROJECT }} # ID do Projeto GCP
  GAR_LOCATION: us-central1              # Região
  REPOSITORY: ml-api-repo               # Nome do Artifact Registry
  SERVICE: ml-api-service               # Nome do Serviço Cloud Run
  REGION: us-central1                   # Região do Deploy

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write' # Obrigatório para WIF

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v3
        with:
          token_format: access_token
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - name: Docker Auth
        uses: docker/login-action@v3
        with:
          username: 'oauth2accesstoken'
          password: ${{ steps.auth.outputs.access_token }}
          registry: ${{ env.GAR_LOCATION }}-docker.pkg.dev

      - name: Build and Push Container
        run: |-
          docker build -t "${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}" ./
          docker push "${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}"

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v3
        with:
          service: ${{ env.SERVICE }}
          region: ${{ env.REGION }}
          image: ${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE }}:${{ github.sha }}
```

---

## Como verificar se o Deploy funcionou?

Após o pipeline brilhar em verde no GitHub:

1. Vá ao console do **Cloud Run**.
2. Clique no seu serviço e copie a **URL** gerada.
3. Teste no seu terminal:
   ```bash
   curl https://sua-url-aqui.run.app/
   # Resposta esperada: {"status": "online", "service": "ML API"}
   ```

## Referências e Indicações

Para quem quiser mergulhar ainda mais fundo na documentação oficial:

- **Workload Identity Federation com GitHub Actions:** [Documentação Oficial GCP](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines?hl=pt-br#github-actions)
- **Deploy no Cloud Run via GitHub Actions:** [GitHub Actions Marketplace](https://github.com/marketplace/actions/deploy-to-cloud-run)
- **GitHub Auth Action (OIDC):** [google-github-actions/auth](https://github.com/google-github-actions/auth)
- **Guia de IAM do Cloud Run:** [Permissões de Deploy](https://cloud.google.com/run/docs/deploying)
- **Diferenças entre Artifact Registry e Container Registry:** [Blog do Google Cloud](https://cloud.google.com/blog/products/application-development/understanding-artifact-registry-vs-container-registry)

---

## Conclusão

Este fluxo garante que seu modelo de ML saia do seu computador direto para uma infraestrutura escalável, segura e profissional. Com o WIF, você dorme tranquilo sabendo que não há chaves estáticas do seu projeto flutuando por aí!

Espero que este guia ajude você a colocar seu projeto no ar! Alguma dúvida? Deixe nos comentários.
