# Use uma imagem base oficial do Python
FROM python:3.10-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie apenas os arquivos de dependência primeiro, para aproveitar o cache do Docker
COPY pyproject.toml poetry.lock ./

# Instale o Poetry
RUN pip install poetry

# Instale as dependências do projeto
RUN poetry install --no-dev

# Copie o restante do código do aplicativo
COPY . .

# Exponha a porta em que a aplicação irá rodar
EXPOSE 5000

# Defina a variável de ambiente para indicar o ambiente de produção
ENV FLASK_ENV=production

# Comando para rodar a aplicação
CMD ["poetry", "run", "python", "app.py"]
