from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return jsonify({
        "name": "TeleshopNews API",
        "status": "active",
        "endpoints": {
            "/api/news": "Barcha yangiliklar",
            "/api/health": "Server holati"
        }
    })


@app.route("/api/news")
def news():
    if not os.path.exists("news_data.json"):
        return jsonify({"success": False, "message": "Ma'lumot yo‘q"})

    with open("news_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "file_exists": os.path.exists("news_data.json")
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
