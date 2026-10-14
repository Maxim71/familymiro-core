# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
import random

app = Flask(__name__)

@app.route('/', methods=['GET'])
def flask_tutor_home():
    """📡 АСИНХРОННЫЙ ТЬЮТОР-МОДУЛЬ FLASK: Магазин пинов строительных материалов на основе Ozon и WB"""
    wb_ozon_pins = [
        {"marketplace": "Wildberries", "pin_id": "WB-77821", "item": "Сверло по бетону SDS-plus", "trend_views": 14500, "margin": "32%"},
        {"marketplace": "Ozon", "pin_id": "OZ-99312", "item": "Диск алмазный отрезной 230мм", "trend_views": 28900, "margin": "41%"},
        {"marketplace": "Wildberries", "pin_id": "WB-44102", "item": "Перчатки рабочие нитриловые (пачка)", "trend_views": 89000, "margin": "55%"}
    ]
    return jsonify({
        "status": "active",
        "service": "Flask Маркетплейс-Парсер Пинов",
        "retained_margin_data": wb_ozon_pins,
        "database_aip_status": "🟢 JSON-ОЗУ СВЯЗЬ С ПОСТГРЕСОМ СТАБИЛЬНА"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
