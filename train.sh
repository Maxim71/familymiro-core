#!/bin/bash
# Скрипт управления ИТР-платформой "Бронепоезд" (SAAS-Колесо)

case "$1" in
  start)
    echo "=== ЗАПУСК ТРИАДЫ (ВЕЧНОСТЬ И СТРОЙКА) ==="
    docker start miro_postgres_evolution miro_redis_broker miro_web_monolith
    ;;
  stop)
    echo "=== ЗАКРЫТИЕ ПЛАТФОРМЫ ==="
    docker stop miro_web_monolith miro_redis_broker miro_postgres_evolution
    ;;
  status)
    echo "=== МОНИТОРИНГ КОНТУРА (ЗРЕНИЕ СОКОЛА) ==="
    docker ps --filter "name=miro_"
    ;;
  heal)
    echo "=== ЛЕЧЕНИЕ СИСТЕМЫ И СБОР СТАТИКИ ==="
    docker exec -it miro_web_monolith sh -c "python manage.py collectstatic --noinput && python manage.py migrate"
    ;;
  deploy)
    echo "=== РЕЖИССЕР: CI/CD ОБНОВЛЕНИЕ НА ЛЕТУ ==="
    git pull origin main
    docker restart miro_web_monolith
    echo "Платформа успешно обновлена без потери данных ВЕЧНОСТИ."
    ;;
  *)
    echo "Использование: ./train.sh {start|stop|status|heal|deploy}"
    ;;
esac
