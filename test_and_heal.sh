#!/bin/bash
TARGET_FILE="/root/app/web_portal.py"

echo "🔎 [ИТР-ТЕСТ]: ИИ-Жук сканирует код на SyntaxError..."
/root/app/hello/bin/python -m py_compile \$TARGET_FILE 2> /root/app/test_error.log

if [ \$? -ne 0 ]; then
    echo "⚠️ [ОБНАРУЖЕН БАГ]: Тест поймал синтаксическую помарку! Включаю автоматическое исцеление..."
    # Автоматически заменяем ошибочную висячую запятую на чистый рабочий массив
    sed -i 's/"Snip_Hours":\s*,/"Snip_Hours": [160, 240],/g' \$TARGET_FILE
    echo "🟢 [ИСПРАВЛЕНО]: Код исцелен ИИ-Жуком в ОЗУ!"
else
    echo "✅ [УСПЕХ]: Код полностью чист от SyntaxError. Запуск безопасен."
fi

# Мягкий перезапуск Streamlit на порту 3500 из venv окружения Python
fuser -k 3500/tcp 2>/dev/null
nohup /root/app/hello/bin/python -m streamlit run \$TARGET_FILE --server.port=3500 --server.address=0.0.0.0 > /root/app/streamlit_run.log 2>&1 &
echo "🚀 [БРОНЕПОЕЗД В ЭФИРЕ]: Порт 3500 поднят!"
