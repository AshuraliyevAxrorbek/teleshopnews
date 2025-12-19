from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Barcha domenlardan ruxsat

@app.route('/')
def index():
    """API asosiy sahifa"""
    return jsonify({
        'name': 'TeleshopNews API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            '/api/news': 'Barcha yangiliklar',
            '/api/health': 'Server holati'
        }
    })

@app.route('/api/news')
def get_news():
    """Yangiliklar API"""
    try:
        # news_data.json faylini o'qish
        if os.path.exists('news_data.json'):
            with open('news_data.json', 'r', encoding='utf-8') as f:
                news = json.load(f)
            
            return jsonify({
                'success': True,
                'data': news,
                'count': len(news),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ma\'lumotlar fayli topilmadi',
                'message': 'Parser ishga tushmagan bo\'lishi mumkin'
            }), 404
            
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'JSON fayl buzilgan'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health():
    """Server holati"""
    try:
        # Fayl mavjudligini tekshirish
        file_exists = os.path.exists('news_data.json')
        
        news_count = 0
        if file_exists:
            with open('news_data.json', 'r', encoding='utf-8') as f:
                news = json.load(f)
                news_count = len(news)
        
        return jsonify({
            'status': 'healthy',
            'file_exists': file_exists,
            'news_count': news_count,
            'timestamp': datetime.now().isoformat()
        })
    except:
        return jsonify({
            'status': 'unhealthy'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint topilmadi'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Server xatosi'
    }), 500

if __name__ == '__main__':
    # Port muhit o'zgaruvchisidan yoki 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
