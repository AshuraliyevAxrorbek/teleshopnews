from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import time
from datetime import datetime

# 👉 parser funksiyasini chaqiramiz
from parser import run_parser

app = Flask(__name__)
CORS(app)

DATA_FILE = "news_data.json"

# ⏱ Parser interval (30 daqiqa)
PARSER_INTERVAL = 60 * 30
LAST_RUN = 0


# ================= ROOT =================

@app.route("/")
def index():
    return jsonify({
        "name": "TeleshopNews API",
        "status": "active",
        "mode": "free-parser-trigger",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "/api/news": "Yangiliklar (page, limit, category)",
            "/api/health": "Server holati"
        }
    })


# ================= NEWS =================

@app.route("/api/news")
def get_news():
    global LAST_RUN

    # 🔥 HAR 30 DAQIQADA PARSER
    now = time.time()
    if now - LAST_RUN > PARSER_INTERVAL:
        try:
            run_parser()
            LAST_RUN = now
        except Exception as e:
            print("❌ Parser xato:", e)

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

    # ================= PARAMS =================
    page = request.args.get("page", type=int, default=1)
    limit = request.args.get("limit", type=int)
    category = request.args.get("category")

    if page < 1:
        page = 1

    # ================= FILTER =================
    if category:
        data = [item for item in data if item.get("category") == category]

    total = len(data)

    # ================= PAGINATION =================
    if limit is not None:
        if limit < 1 or limit > 200:
            limit = 15

        start = (page - 1) * limit
        end = start + limit
        sliced_data = data[start:end]
    else:
        # 🔥 LIMIT YO‘Q → HAMMASI
        sliced_data = data

    return jsonify({
        "success": True,
        "count": total,
        "page": page,
        "limit": limit,
        "data": sliced_data,
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
        ),
        "parser_interval_minutes": PARSER_INTERVAL // 60
    })


# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

