# Use uma imagem base do Python
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    wget \
    unzip \
    gnupg \
    apt-transport-https \
    ca-certificates \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y wget gnupg2 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get install -yqq unzip \
    && wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.72/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/


# Set display port to avoid crash
ENV DISPLAY=:99


# Defina o diretório de trabalho
WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf

# Copie os arquivos de requisitos e instale as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código para o contêiner
COPY . .


# Instale o Supervisor
RUN apt-get update && apt-get install -y supervisor

# Configure o Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/log/nginx && chown -R www-data:www-data /var/log/nginx

# Exponha a porta 9001 para o Supervisor
EXPOSE 9001

# Defina o comando para iniciar o Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
