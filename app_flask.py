# -*- coding: utf-8 -*-
from flask import Flask
app = Flask("Miro_Flask")
@app.route("/")
def hi(): return "Flask Active"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
