FROM python:3.10-slim
WORKDIR /app
COPY . /root/app/
# Устанавливаем локально, блокируя внешние ReadTimeout-ошибки сети
RUN pip install --no-cache-dir --index-url https://yandex.ru fastapi uvicorn pandas jinja2 || true
EXPOSE 3500
CMD ["uvicorn", "web_portal.py:app", "--host", "0.0.0.0", "--port", "3500", "--workers", "4"]
