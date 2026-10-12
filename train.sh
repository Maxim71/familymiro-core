#!/bin/bash
# Скрипт управления ИТР-платформой "Бронепоезд" (Familymira Монолит + FastAPI OPC)

case "$1" in
  start)
    echo "=== [РЕЖИССЕР] ЗАПУСК ПАРАЛЛЕЛЬНЫХ ПРОЦЕССОВ ==="
    
    # 1. Запуск асинхронного FastAPI шлюза
    source ~/app/hello/bin/activate
    pkill -f "uvicorn ezhik_api:app"
    nohup uvicorn ezhik_api:app --host 0.0.0.0 --port 8050 --reload > uvicorn_ezhik.log 2>&1 &
    echo "[OK] FastAPI успешно поднят на порту 8050."
    
    # 2. Проверка доступности туннеля базы данных PostgreSQL
    echo "Проверка моста к базе данных PostgreSQL (порт 5432)..."
    sleep 2
    if nc -z 127.0.0.1 5432; then
        echo "[OK] SSH-Туннель активен. База данных ВЕЧНОСТИ доступна!"
        echo "Применение миграций в базу данных..."
        python manage.py migrate
    else
        echo "[ВНИМАНИЕ] Порт 5432 закрыт. Напоминание: Запустите обратный туннель на физическом ноутбуке:"
        echo "ssh -f -N -R 5432:127.0.0.1:5432 root@89.111.155.234"
    fi
    ;;
  stop)
    echo "=== ЗАКРЫТИЕ ПЛАТФОРМЫ ==="
    pkill -f "uvicorn ezhik_api:app"
    echo "[OK] Все асинхронные шлюзы остановлены."
    ;;
  status)
    echo "=== МОНИТОРИНГ КОНТУРА СВЯЗИ ==="
    ss -tlnp | grep -E "22|5432|8050"
    ;;
  *)
    echo "Использование: ./train.sh {start|stop|status}"
    ;;
esac
