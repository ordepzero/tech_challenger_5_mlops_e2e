Criar arquivo DockerFile

```
FROM python:3.12.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./src /app/src
COPY ./models /app/models

# Comando padrão para rodar FastAPI
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


Removi a última linha do arquivo de requirements.txt
```
-e .
```

Criar a image docker
```
docker build -t ml-api .
```

Criar container com a imagem
```
docker run -p 8000:8000 ml-api
```

Testar o container acessando a url
```
http://localhost:8000/
```

Para realizar o deplou no Cloud Run é necessário

Ativar a API do container registry.
![alt text](image-10.png)


Executar o comando no terminal da máquina local para configurar a autenticação
```
gcloud auth configure-docker
```

É preciso atribuir uma TAG à imagem que é o caminho da imagem no container registry que é o formato
```
gcr.io/<id_projeto_gcr>/<nome_imagem_docker>
```

Este é o nome final
```
docker tag ml-api  gcr.io/project-28f296f3-806a-47c3-941/ml-api
```

Enviar a imagem para o container registry da GCP
```
docker push gcr.io/project-28f296f3-806a-47c3-941/ml-api
```

Imagem se encontra no container registry
![alt text](image-11.png)

Agora vamos usar essa imagem e fazer o deploy com Cloud Run.
- Acesse o Cloud Run, clica em criar um novo serviço.
- Selecionar a opção container, seleciona a image que foi carregada.
- Configura a porta que será usada pelo container: 8000
- Clica em criar e acessa a url que é apresentada no console.
![alt text](image-12.png)
