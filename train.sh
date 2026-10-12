#!/bin/bash
# Скрипт управления ИТР-платформой "Бронепоезд" (SAAS-Колесо + FastAPI OPC)

case "$1" in
  start)
    echo "=== ЗАПУСК ТРИАДЫ КОНТЕЙНЕРОВ ==="
    docker start miro_postgres_evolution miro_redis_broker miro_web_monolith
    
    echo "=== РЕЖИССЕР: ЗАПУСК FASTAPI OPC ШЛЮЗА ==="
    source ~/app/hello/bin/activate
    nohup uvicorn ezhik_api.py:app --host 0.0.0.0 --port 8050 --reload > uvicorn_ezhik.log 2>&1 &
    echo "FastAPI успешно поднят на порту 8050."
    ;;
  stop)
    echo "=== ЗАКРЫТИЕ ПЛАТФОРМЫ ==="
    docker stop miro_web_monolith miro_redis_broker miro_postgres_evolution
    echo "=== ОСТАНОВКА FASTAPI ШЛЮЗА ==="
    pkill -f "uvicorn ezhik_api.py:app"
    ;;
  status)
    echo "=== МОНИТОРИНГ КОНТУРА ==="
    docker ps --filter "name=miro_"
    echo "--- Статус FastAPI процессов ---"
    ps aux | grep uvicorn
    ;;
  heal)
    echo "=== ЛЕЧЕНИЕ СИСТЕМЫ ==="
    docker exec -it miro_web_monolith sh -c "python manage.py collectstatic --noinput && python manage.py migrate"
    ;;
  *)
    echo "Использование: ./train.sh {start|stop|status|heal}"
    ;;
esac
