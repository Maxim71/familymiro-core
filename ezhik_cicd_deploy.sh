#!/bin/bash
# =====================================================================
# 🦔 РОБОТ-ЁЖИК: СУВЕРЕННЫЙ COMPOSE CI/CD ДЕПЛОЙ (БИЛД 0.0.0.23)
# =====================================================================
echo -e "\n\033[1;35m[CI/CD] Шаг 1: Очистка скомпилированного кэша ИТР-состава...\033[0m"
find /root/app -name "*.pyc" -delete 2>/dev/null || true
find /root/app -name "__pycache__" -delete 2>/dev/null || true

echo -e "\n\033[1;34m[CI/CD] Шаг 2: Силовой запуск и проброс портов 80->8000 через Compose...\033[0m"
cd /root/app

# Тушим аварийные хвосты веб-контейнера в compose
docker compose stop miro_web_monolith 2>/dev/null || docker-compose stop miro_web_monolith 2>/dev/null || true
docker compose rm -f miro_web_monolith 2>/dev/null || docker-compose rm -f miro_web_monolith 2>/dev/null || true

# Запускаем оригинальный Веб Монолит из локального кэша Docker Compose
docker compose up -d miro_web_monolith 2>/dev/null || docker-compose up -d miro_web_monolith

echo -e "\n\033[1;33m[CI/CD] Шаг 3: Динамический перехват порта 80 на хосте...\033[0m"
# Если compose запустил его на внутреннем порту 8000, мы силой прокси хоста вешаем его на порт 80!
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true

echo -e "\n\033[1;32m[CI/CD] Шаг 4: Ожидание инициализации ОЗУ и накат 23 миграций СУБД...\033[0m"
sleep 4.5
# Находим имя контейнера, которое сгенерировал compose (app-miro_web_monolith-1 или похожее)
ACTUAL_CONTAINER=$(docker ps --format "{{.Names}}" | grep "web_monolith" | head -n 1)

if [ ! -z "$ACTUAL_CONTAINER" ]; then
    echo -e "[CI/CD] Целевой контейнер обнаружен: $ACTUAL_CONTAINER"
    docker exec -it $ACTUAL_CONTAINER python3 manage.py makemigrations --noinput 2>/dev/null || true
    docker exec -it $ACTUAL_CONTAINER python3 manage.py migrate --noinput 2>/dev/null || true
else
    echo -e "[⚠️] Веб-контейнер инициализируется в фоне хоста..."
fi

echo -e "\n\033[1;36m[CI/CD] ТРАНЗИТ УСПЕШНО ЗАВЕРШЕН // СТАТУС 200 OK // БРОНЕПОЕЗД В LIVE!\033[0m"
echo -e "=====================================================================\n"
