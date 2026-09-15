FROM python:3.10-slim

# Ставим железные графические руки для видеоплееров прораба, gcc и OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Обновляем pip и накатываем все твои b2b-библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir django opencv-python Pillow python-dotenv django-sslserver confluent-kafka

# Закидываем весь твой 1700-строчный Грааль в контейнер
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload", "--nostatic"]
