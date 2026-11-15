FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir ultralytics opencv-python-headless

COPY . .

# Asegurar directorios de almacenamiento y pesos y permisos del entrypoint
RUN mkdir -p storage/imagenes app/ml/pesos && chmod +x entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
