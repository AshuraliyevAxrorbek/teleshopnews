import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime
import time
import re
import os

def translate_to_uzbek(text):
    """Bepul va manoli tarjima"""
    try:
        if not text or len(text) < 3:
            return text
            
        translator = GoogleTranslator(source='en', target='uz')
        
        # Uzun matnlarni bo'lib tarjima qilish
        if len(text) > 4500:
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated = ' '.join([translator.translate(chunk) for chunk in chunks])
        else:
            translated = translator.translate(text)
        
        return translated
    except Exception as e:
        print(f"⚠️ Tarjima xatosi: {e}")
        return text

def clean_text(text):
    """Matnni tozalash"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def parse_time(time_str):
    """Vaqtni soatlarga o'girish"""
    try:
        if not time_str:
            return 0
            
        time_lower = time_str.lower()
        
        if 'hour' in time_lower or 'soat' in time_lower:
            hours = int(''.join(filter(str.isdigit, time_str.split()[0])))
            return hours
        elif 'day' in time_lower or 'kun' in time_lower:
            days = int(''.join(filter(str.isdigit, time_str.split()[0])))
            return days * 24
        elif 'min' in time_lower or 'daqiqa' in time_lower:
            return 0
        elif 'week' in time_lower or 'hafta' in time_lower:
            weeks = int(''.join(filter(str.isdigit, time_str.split()[0])))
            return weeks * 168
        else:
            return 0
    except:
        return 0

def detect_category(title):
    """Kategoriya aniqlash"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['samsung', 'galaxy']):
        return 'Samsung'
    elif any(word in title_lower for word in ['iphone', 'apple', 'ios']):
        return 'Apple'
    elif any(word in title_lower for word in ['xiaomi', 'redmi', 'poco']):
        return 'Xiaomi'
    elif any(word in title_lower for word in ['oneplus']):
        return 'OnePlus'
    elif any(word in title_lower for word in ['oppo', 'realme']):
        return 'Oppo'
    elif any(word in title_lower for word in ['vivo', 'iqoo']):
        return 'Vivo'
    elif any(word in title_lower for word in ['google', 'pixel']):
        return 'Google'
    elif any(word in title_lower for word in ['huawei', 'honor']):
        return 'Huawei'
    else:
        return 'Boshqa'

def parse_gsmarena():
    """GSMArena dan yangiliklar parsing"""
    print("🌐 GSMArena ga ulanilmoqda...")
    
    url = "https://www.gsmarena.com/news.php3"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news_list = []
        
        # Yangiliklar konteynerini topish
        news_section = soup.find('div', class_='news-item') or soup.find('div', {'id': 'body'})
        
        if not news_section:
            print("❌ Yangiliklar konteyneri topilmadi")
            return []
        
        # Barcha yangilik elementlarini topish
        news_items = soup.find_all('li')[:30]  # Oxirgi 30ta
        
        print(f"📋 {len(news_items)} ta element topildi")
        
        for idx, item in enumerate(news_items):
            try:
                # Link va sarlavha
                link_tag = item.find('a', href=True)
                if not link_tag:
                    continue
                
                title_en = clean_text(link_tag.get_text())
                
                # Juda qisqa sarlavhalarni o'tkazib yuborish
                if len(title_en) < 15:
                    continue
                
                link = link_tag['href']
                if not link.startswith('http'):
                    link = 'https://www.gsmarena.com/' + link
                
                # Rasm
                img_tag = item.find('img')
                img_url = ''
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    if img_url and not img_url.startswith('http'):
                        img_url = 'https://www.gsmarena.com/' + img_url
                
                # Vaqt va tavsif
                time_str = 'Yangi'
                desc_en = ''
                
                # Span taglardan ma'lumot olish
                spans = item.find_all('span')
                for span in spans:
                    text = clean_text(span.get_text())
                    if any(word in text.lower() for word in ['hour', 'day', 'min', 'week', 'ago']):
                        time_str = text
                    elif len(text) > 30:
                        desc_en = text
                
                # Agar tavsif topilmasa, p tagdan izlash
                if not desc_en:
                    p_tag = item.find('p')
                    if p_tag:
                        desc_en = clean_text(p_tag.get_text())
                
                # O'zbekchaga tarjima qilish
                print(f"🔄 [{idx+1}] Tarjima: {title_en[:50]}...")
                title_uz = translate_to_uzbek(title_en)
                time.sleep(0.3)  # Rate limiting
                
                desc_uz = ''
                if desc_en and len(desc_en) > 10:
                    desc_uz = translate_to_uzbek(desc_en)
                    time.sleep(0.3)
                
                # Vaqtni hisoblash
                hours_ago = parse_time(time_str)
                
                # Yangilik obyekti
                news_item = {
                    'id': abs(hash(title_en + link)),
                    'title_en': title_en,
                    'title_uz': title_uz,
                    'desc_en': desc_en,
                    'desc_uz': desc_uz,
                    'image': img_url,
                    'link': link,
                    'time': time_str,
                    'hours_ago': hours_ago,
                    'timestamp': datetime.now().isoformat(),
                    'is_new': hours_ago <= 10,
                    'category': detect_category(title_en)
                }
                
                news_list.append(news_item)
                print(f"✅ [{idx+1}] Saqlandi: {title_uz[:50]}...")
                
            except Exception as e:
                print(f"⚠️ Element parsing xatosi: {e}")
                continue
        
        return news_list
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Internet xatosi: {e}")
        return []
    except Exception as e:
        print(f"❌ Umumiy xato: {e}")
        return []

def save_news(news_list):
    """Yangiliklar JSON faylga saqlash"""
    try:
        # news_data.json faylini yaratish
        with open('news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"💾 {len(news_list)} ta yangilik saqlandi!")
        return True
    except Exception as e:
        print(f"❌ Saqlash xatosi: {e}")
        return False

def main():
    """Asosiy funksiya"""
    print("=" * 60)
    print("📱 TELESHOPNEWS - YANGILIKLAR PARSER")
    print("=" * 60)
    print()
    
    # Yangiliklar parsing
    news = parse_gsmarena()
    
    if news and len(news) > 0:
        print(f"\n✅ Jami {len(news)} ta yangilik topildi!")
        
        # Saqlash
        if save_news(news):
            print("✅ Barcha yangiliklar muvaffaqiyatli saqlandi!")
            
            # Statistika
            new_count = len([n for n in news if n['is_new']])
            print(f"\n📊 STATISTIKA:")
            print(f"   • Jami: {len(news)} ta")
            print(f"   • Yangi: {new_count} ta")
            print(f"   • Kategoriyalar: {len(set(n['category'] for n in news))} ta")
        else:
            print("❌ Saqlashda xatolik!")
    else:
        print("❌ Yangiliklar topilmadi!")
        
        # Demo ma'lumot yaratish (test uchun)
        print("ℹ️ Demo ma'lumotlar yaratilmoqda...")
        demo_news = [
            {
                'id': 1,
                'title_en': 'Samsung Galaxy S24 Ultra Review',
                'title_uz': 'Samsung Galaxy S24 Ultra Sharhi',
                'desc_en': 'Full review of the latest Samsung flagship',
                'desc_uz': 'Eng yangi Samsung flagmanining to\'liq sharhi',
                'image': 'https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-ultra-5g.jpg',
                'link': 'https://www.gsmarena.com/',
                'time': '2 hours ago',
                'hours_ago': 2,
                'timestamp': datetime.now().isoformat(),
                'is_new': True,
                'category': 'Samsung'
            }
        ]
        save_news(demo_news)

if __name__ == '__main__':
    main()
