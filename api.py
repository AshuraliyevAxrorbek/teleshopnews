from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "news_data.json"


# ================= ROOT =================

@app.route("/")
def index():
    return jsonify({
        "name": "TeleshopNews API",
        "status": "active",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "/api/news": "Yangiliklar (page, limit, category)",
            "/api/health": "Server holati"
        }
    })


# ================= NEWS =================

@app.route("/api/news")
def get_news():
    if not os.path.exists(DATA_FILE):
        return jsonify({
            "success": False,
            "message": "Ma'lumotlar hali mavjud emas"
        }), 404

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Faylni o‘qishda xato",
            "error": str(e)
        }), 500

    # Query params
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 15))
    except ValueError:
        page = 1
        limit = 15

    category = request.args.get("category")

    if page < 1:
        page = 1
    if limit < 1 or limit > 50:
        limit = 15

    # Filter by category
    if category:
        data = [item for item in data if item.get("category") == category]

    total = len(data)
    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        "success": True,
        "count": total,
        "page": page,
        "limit": limit,
        "data": data[start:end],
        "timestamp": datetime.now().isoformat()
    })


# ================= HEALTH =================

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "file_exists": os.path.exists(DATA_FILE),
        "last_update": (
            datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).isoformat()
            if os.path.exists(DATA_FILE) else None
        )
    })


# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
