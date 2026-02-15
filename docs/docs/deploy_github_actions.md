Criar o diretório .github/workflows
Criar o arquivo cloud_run.yaml neste diretório baseado no [cloudrun-docker.yml](https://github.com/google-github-actions/example-workflows/blob/main/workflows/deploy-cloudrun/cloudrun-docker.yml) oficial do google


Configurar Workload Identity Pool no console para permitir o GitHub realizar a integração de acordo com a página [Configurar a federação de identidade](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines?hl=pt-br#github-actions)

No GitHub, acessei o Settings do projeto para criar os secrets.

```
PROJECT_ID: ${{ secret.RUN_PROJECT }}
GAR_LOCATION: ${{ secret.GAR_LOCATION }}
REPOSITORY: ${{ secret.REPOSITORY_NAME }}
SERVICE: ${{ secret.SERVICE_NAME }}
REGION: ${{ secret.SERVICE_REGION }}
```