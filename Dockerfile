FROM python:3.10-slim
WORKDIR /app
COPY style.css /app/style.css
COPY web_portal.py /app/web_portal.py
COPY core_director.py /app/core_director.py
COPY core_rollback.py /app/core_rollback.py
RUN pip install --timeout=100 --no-cache-dir --index-url https://yandex.ru streamlit==1.32.0 pandas==2.2.0 pillow==10.2.0
EXPOSE 3500
CMD ["streamlit", "run", "web_portal.py", "--server.port=3500", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.maxUploadSize=2048"]
