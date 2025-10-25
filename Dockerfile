# Imagen base ligera de Python 3.11
FROM python:3.11-slim

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias (Postgres, compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias primero (optimiza cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Copiar archivo .env (si quieres usarlo dentro del contenedor)
# En producción normalmente se usan variables de entorno inyectadas por la plataforma
COPY .env .env

# Exponer el puerto donde corre FastAPI
EXPOSE 8000

# Comando para ejecutar la app con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
