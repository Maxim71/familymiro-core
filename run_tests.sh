#!/bin/bash
# Автоматический тест ИТР-контура платформы FamilyMira

echo "=== ЗАПУСК АВТОМАТИЧЕСКИХ ТЕСТОВ СИСТЕМЫ ==="

# 1. Проверяем доступность FastAPI (Порт 8050)
echo "Проверка FastAPI OPC-шлюза..."
FASTAPI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0 || echo "DOWN")

if [ "$FASTAPI_STATUS" == "405" ] || [ "$FASTAPI_STATUS" == "200" ]; then
    echo "[OK] FastAPI шлюз активен и слушает порт 8050."
else
    echo "[FAIL] FastAPI шлюз недоступен (Код: $FASTAPI_STATUS). Запустите его через ./train.sh start."
fi

# 2. Проверяем работу ИИ-парсера спецификаций
echo "Тестирование распознавания чертежей Ёжиком..."
TEST_RESPONSE=$(curl -s -X 'POST' 'http://127.0.0' \
  -H 'Content-Type: application/json' \
  -d '{"filename": "64-ЭОМ.ЦОД_Спецификация.pdf", "pin_code": "BLOGGER_CYBER_2026"}')

if [[ $TEST_RESPONSE == *"success"* ]]; then
    echo "[OK] Интеллект Ёжика успешно распознал шифр и выдал логистику затрат партнеров."
else
    echo "[FAIL] Сбой парсера ИИ. Ответ сервера: $TEST_RESPONSE"
fi
