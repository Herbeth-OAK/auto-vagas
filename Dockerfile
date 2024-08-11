# Use a imagem oficial do Python como base
FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Cria diretórios para o app e configurações
WORKDIR /app

# Copia o arquivo de dependências e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto para o container
COPY . .


# Adicione esta linha ao Dockerfile
COPY session_name.session /app/session_name.session

# Configura o Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponha a porta do Nginx
EXPOSE 80

# Comando de entrada do Supervisor
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
