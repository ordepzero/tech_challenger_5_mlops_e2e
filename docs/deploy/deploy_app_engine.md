Neste tutorial será apresentado o deploy usando o SDK do GCP (gcloud).

Link dos passos a instalação do SDK: https://docs.cloud.google.com/sdk/docs/install-sdk?hl=pt-br#windows

Baixei o instalador, executei.

Precisei executar alguns comandos adicionais para executar no bash
```
export PATH=$PATH:"/c/Program Files (x86)/Google/Cloud SDK/google-cloud-sdk/bin"
source ~/.bashrc
gcloud --version
```


Importante nos testes locais estar com o ambiente virtual ativado.


Precisamos criar o arquivo app.yaml na raiz do projeto.
```
runtime: python
env: flex
entrypoint: uvicorn -b :$UVICORN_PORT main:app

runtime_config:
    python_version: 3

includes:
- env_vars.yaml
```

Criar o arquivo env_vars.yaml na raiz do projeto:
```
env_variables:
    UVICORN_HOST: 0.0.0.0
    UVICORN_PORT: 8000
```

Definir as variáveis de ambiente:

Usando terminal bash:
```
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000

uvicorn main:app --host $UVICORN_HOST --port $UVICORN_PORT
```

Precisamos colocar o arquivo src/app/main.py na raiz do projeto também.

Depois executar o comando:
```
gcloud app deploy
```

ou com debug (dica: aqui é realmente verboso)
```
gcloud app deploy --verbosity=debug
```

Executei o seguinte comando para entender as permissões
```
gcloud app describe
```

Precisei rodar o comando para dar permissão de acessar o bucket
```
gcloud projects add-iam-policy-binding project-28f296f3-806a-47c3-941 \
  --member="serviceAccount:project-28f296f3-806a-47c3-941@appspot.gserviceaccount.com" \
  --role="roles/storage.admin"
```