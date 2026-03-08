FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p data
COPY feature_repo/ ./feature_repo/

EXPOSE 8000

CMD ["python", "src/api/main.py"]