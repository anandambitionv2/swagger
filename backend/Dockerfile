FROM python:3.12-slim

WORKDIR /app

# Install native dependencies and dynamically add the correct MS SQL repo architecture
RUN apt-get update && \
    apt-get install -y curl gnupg unixodbc unixodbc-dev dpkg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    # 🌟 FIX: Use $(dpkg --print-architecture) instead of hardcoded 'amd64'
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app.py .

EXPOSE 5000

CMD ["python", "app.py"]
