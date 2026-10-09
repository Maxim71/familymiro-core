from flask import Flask, jsonify
app = Flask(__name__)

LAVA_SHARE_PERCENT = 4.0

@app.route('/promo/blogger/<blogger_name>')
def welcome_blogger_landing(blogger_name):
    return jsonify({
        "status": "success",
        "message": f"Добро пожаловать в Синдикат, {blogger_name}! Твой суверенный блог активирован.",
        "design_style": "🎨 Pinterest-Слой 2.0 (Адаптивная плиточная фотофиксация)",
        "monetization": f"💳 Выплаты автоматизированы через LAVA API. Доля Создателя: {LAVA_SHARE_PERCENT}%"
    })

@app.route('/promo/health')
def health_check():
    return jsonify({"status": "Up", "msg": "Flask-ракета полностью стабильна в ОЗУ."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
