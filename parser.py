import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime
import time
import re
import os

BASE_URL = "https://gagadget.com"
LIST_URL = "https://gagadget.com/news/phones/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ru-RU,ru;q=0.9"
}

translator = GoogleTranslator(source="ru", target="uz")


def detect_category(title: str):
    t = title.lower()

    if "samsung" in t or "galaxy" in t:
        return "Samsung"
    if "apple" in t or "iphone" in t:
        return "Apple"
    if "xiaomi" in t or "redmi" in t or "poco" in t:
        return "Xiaomi"
    if "google" in t or "pixel" in t:
        return "Google"
    if "oneplus" in t:
        return "OnePlus"

    return "Boshqa"


# ================= UTIL =================

def clean(text):
    return re.sub(r"\s+", " ", text).strip() if text else ""


def translate(text):
    try:
        if not text or len(text) < 5:
            return text
        if len(text) > 4500:
            parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
            return " ".join(translator.translate(p) for p in parts)
        return translator.translate(text)
    except:
        return text


def parse_hours(text):
    t = text.lower()
    nums = re.findall(r"\d+", t)
    if not nums:
        return 0
    n = int(nums[0])
    if "час" in t:
        return n
    if "день" in t:
        return n * 24
    return 0


# ================= ARTICLE =================

def fetch_article(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    body = soup.select_one("div.b-font-def")
    if not body:
        return "", []

    paragraphs = [
        clean(p.text)
        for p in body.find_all("p")
        if len(p.text.strip()) > 40
    ]

    images = []
    for img in body.find_all("img"):
        src = img.get("src")
        if src and "logo" not in src and "icon" not in src:
            if src.startswith("/"):
                src = BASE_URL + src
            images.append(src)

    return "\n\n".join(paragraphs), images


# ================= MAIN PARSER =================

def parse_gagadget():
    print("🌐 Gagadget phones parsing...")

    r = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("div.l-grid_3")
    print(f"📋 Topildi: {len(cards)} ta")

    news = []

    for i, card in enumerate(cards[:15], 1):
        try:
            title_a = card.select_one("span.cell-title a")
            if not title_a:
                continue

            title_ru = clean(title_a.text)
            link = BASE_URL + title_a["href"]

            img = card.select_one("a.cell-img img")
            image = ""
            if img and img.get("src"):
                image = BASE_URL + img["src"]

            date = card.select_one("span.cell-date")
            time_text = clean(date.text) if date else "0 часов назад"
            hours = parse_hours(time_text)

            print(f"🔹 {i}. {title_ru}")

            full_ru, article_images = fetch_article(link)

            news.append({
                "id": abs(hash(link)),

                "title_uz": translate(title_ru),
                "desc_uz": translate(title_ru),
                "full_text_uz": translate(full_ru),

                "title_en": title_ru,
                "desc_en": title_ru,
                "full_text_en": full_ru,

                "image": image,
                "article_images": article_images,

                "category": detect_category(title_ru),  # 🔥 MUHIM JOY
                "link": link,
                "time": time_text,
                "hours_ago": hours,
                "is_new": hours <= 24,

                "timestamp": datetime.now().isoformat()
            })



            time.sleep(1)

        except Exception as e:
            print("Xato:", e)

    return news


# ================= SAVE =================

def save_news(news):
    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saqlandi: {len(news)} ta yangilik")


def main():
    news = parse_gagadget()
    save_news(news)


if __name__ == "__main__":
    main()
