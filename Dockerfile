# 1. Imagen base: Usamos la versión slim para que sea ligera y eficiente
FROM python:3.12-slim

# 2. Variables de entorno para mejorar el rendimiento de Python en contenedores
# Evita que Python genere archivos .pyc y permite ver los logs al instante
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalación de dependencias del sistema para el procesamiento de imágenes (Pillow)
# Se limpian los archivos temporales de apt para mantener la imagen pequeña
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalación de dependencias de Python
# Copiamos primero requirements.txt para aprovechar el sistema de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia del código fuente
# Se copia todo el contenido del contexto de construcción al contenedor
COPY . .

# 7. Puerto en el que corre tu aplicación Flask
EXPOSE 5000

# 8. Comando para iniciar la aplicación
# Asegúrate de que en app.py el host sea '0.0.0.0'
CMD ["python", "app.py"]