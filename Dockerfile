FROM python:3.11-slim
WORKDIR /workspace

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install jinja2 && \
    pip install --no-cache-dir -r requirements.txt

# Copia o .env para dentro do container
COPY .env .env


# Copia tudo para o workspace
COPY . . 

EXPOSE 8000
# Define o PYTHONPATH para garantir que a pasta 'app' seja tratada como módulo
ENV PYTHONPATH=/workspace
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
