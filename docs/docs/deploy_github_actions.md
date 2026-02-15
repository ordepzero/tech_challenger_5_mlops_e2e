Criar o diretório .github/workflows
Criar o arquivo cloud_run.yaml neste diretório baseado no [cloudrun-docker.yml](https://github.com/google-github-actions/example-workflows/blob/main/workflows/deploy-cloudrun/cloudrun-docker.yml) oficial do google


Configurar Workload Identity Pool no console para permitir o GitHub realizar a integração de acordo com a página [Configurar a federação de identidade](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines?hl=pt-br#github-actions)

Criei um service account com a permissão de IODC

Para verificar o WIF_PROVIDER
```
$ gcloud iam workload-identity-pools providers list   --workload-identity-pool=ml-api-pool   --location=global   --project=project-28f296f3-806a-47c3-941
``` 

Resultado apresentado no terminal, usar o valor de `name`
```
---
attributeCondition: assertion.repository=='ordepzero/tech_challenger_5_mlops_e2e'
attributeMapping:
  google.subject: assertion.sub
displayName: github-provider
name: projects/855061287579/locations/global/workloadIdentityPools/ml-api-pool/providers/github
oidc:
  allowedAudiences:
  - https://github.com/ordepzero/tech_challenger_5_mlops_e2e
  issuerUri: https://token.actions.githubusercontent.com
state: ACTIVE
```

Criei o Worload Identity Pools


No GitHub, acessei o Settings do projeto para criar os secrets.

```
PROJECT_ID: ${{ secret.RUN_PROJECT }}
GAR_LOCATION: ${{ secret.GAR_LOCATION }}
REPOSITORY: ${{ secret.REPOSITORY_NAME }}
SERVICE: ${{ secret.SERVICE_NAME }}
REGION: ${{ secret.SERVICE_REGION }}
WIF_PROVIDER: ${{ secrets.WIF_PROVIDER }}
WIF_SERVICE_ACCOUNT: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```