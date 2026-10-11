import os
import sys
import threading
import time
import webview
from django.core.management import execute_from_command_line

def start_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    execute_from_command_line([sys.argv[0], 'runserver', '127.0.0.1:8000', '--nothreading', '--noreload'])

if __name__ == '__main__':
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()
    time.sleep(1)
    
    webview.create_window('Платформа Мироха — ИТР Контур', 'http://127.0.0.1:8000', width=1200, height=800)
    webview.start()
