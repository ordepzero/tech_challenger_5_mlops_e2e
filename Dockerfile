FROM python:3.12.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./src /app/src
COPY ./models /app/models

# Comando padrão para rodar FastAPI
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]