from flask import Flask, render_template, jsonify, request, session
from market_intelligence import MarketIntelligence
from ollama_manager import OllamaManager
from language_manager import LanguageManager
import pandas as pd
import json
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 세션을 위한 시크릿 키
ollama = OllamaManager()
lang_manager = LanguageManager()

# 전역 설정 저장소
current_settings = {
    'api_key': os.getenv('BINANCE_API_KEY', ''),
    'api_secret': os.getenv('BINANCE_SECRET_KEY', ''),
    'use_testnet': False
}

def save_settings_to_env():
    """설정을 .env 파일에 저장"""
    env_path = Path('.env')
    
    # 기존 설정 읽기
    env_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_content[key] = value
    
    # 새 설정 추가/업데이트
    env_content['BINANCE_API_KEY'] = current_settings['api_key']
    env_content['BINANCE_SECRET_KEY'] = current_settings['api_secret']
    
    # 파일에 저장
    with open(env_path, 'w') as f:
        for key, value in env_content.items():
            f.write(f"{key}={value}\n")

@app.route('/')
def index():
    # 세션에서 언어 설정을 가져오거나 기본 언어 사용
    lang_code = session.get('language', lang_manager.get_current_language())
    return render_template('index.html',
                         lang=lang_code,
                         supported_languages=lang_manager.supported_languages,
                         translations=lang_manager.translations[lang_code])

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        data = request.json
        current_settings['api_key'] = data.get('apiKey', '')
        current_settings['api_secret'] = data.get('apiSecret', '')
        current_settings['use_testnet'] = data.get('useTestnet', False)
        
        # 설정을 .env 파일에 저장
        save_settings_to_env()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ollama/status')
def get_ollama_status():
    """Ollama 상태 확인"""
    return jsonify({
        'installed': ollama.is_installed(),
        'running': ollama.is_server_running(),
        'models': ollama.get_installed_models() if ollama.is_server_running() else []
    })

@app.route('/api/ollama/install')
def install_ollama():
    """Ollama 설치"""
    ollama.install_ollama()
    return jsonify({'success': True})

@app.route('/api/ollama/start')
def start_ollama():
    """Ollama 서버 시작"""
    if not ollama.is_installed():
        return jsonify({'success': False, 'error': 'Ollama가 설치되어 있지 않습니다.'})
    
    try:
        ollama.start_server()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ollama/stop')
def stop_ollama():
    """Ollama 서버 중지"""
    try:
        ollama.stop_server()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ollama/models')
def get_models():
    """설치된 모델 목록"""
    if not ollama.is_server_running():
        return jsonify({'success': False, 'error': 'Ollama 서버가 실행 중이지 않습니다.'})
    
    return jsonify({
        'success': True,
        'models': ollama.get_installed_models()
    })

@app.route('/api/ollama/install_model', methods=['POST'])
def install_model():
    """모델 설치"""
    if not ollama.is_server_running():
        return jsonify({'success': False, 'error': 'Ollama 서버가 실행 중이지 않습니다.'})
    
    model_name = request.json.get('model')
    if not model_name:
        return jsonify({'success': False, 'error': '모델 이름이 필요합니다.'})
    
    success = ollama.install_model(model_name)
    return jsonify({'success': success})

@app.route('/api/data')
def get_data():
    try:
        symbol = request.args.get('symbol')
        interval = request.args.get('interval', '1h')
        
        if not symbol:
            return jsonify({'error': '심볼이 필요합니다.'})
            
        # 현재 설정으로 MarketIntelligence 인스턴스 생성
        mi = MarketIntelligence([symbol], 
                              api_key=current_settings['api_key'],
                              api_secret=current_settings['api_secret'],
                              use_testnet=current_settings['use_testnet'])
        
        analysis = mi.get_complete_analysis(symbol, interval=interval)
        df = mi.collector.get_historical_data(symbol, interval=interval)
        
        if df is None or analysis is None:
            return jsonify({'error': '데이터 수집 실패'})
            
        # 캔들스틱 데이터 포맷팅
        candles = []
        for idx, row in df.iterrows():
            candles.append({
                'time': int(idx.timestamp()),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
            
        # MA 데이터 포맷팅
        ma_data = {}
        for period in [5, 10, 30, 60, 90, 120, 240, 360]:
            ma = df['close'].rolling(window=period).mean()
            ma_data[f'ma{period}'] = [
                {'time': int(idx.timestamp()), 'value': float(val)}
                for idx, val in ma.items()
            ]
            
        # BB 데이터 포맷팅
        bb_middle = df['BB_Middle_20'].apply(float)
        bb_upper = df['BB_Upper_20'].apply(float)
        bb_lower = df['BB_Lower_20'].apply(float)
        
        bb_data = {
            'bbMiddle': [
                {'time': int(idx.timestamp()), 'value': val}
                for idx, val in bb_middle.items()
            ],
            'bbUpper': [
                {'time': int(idx.timestamp()), 'value': val}
                for idx, val in bb_upper.items()
            ],
            'bbLower': [
                {'time': int(idx.timestamp()), 'value': val}
                for idx, val in bb_lower.items()
            ]
        }
        
        # RSI 데이터 포맷팅
        rsi_data = [
            {'time': int(idx.timestamp()), 'value': float(val)}
            for idx, val in df['RSI_14'].items()
        ]
        
        return jsonify({
            'candles': candles,
            **ma_data,
            **bb_data,
            'rsi': rsi_data,
            'analysis': analysis['기술적_분석']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/set-language', methods=['POST'])
def set_language():
    """언어 설정을 변경합니다."""
    lang_code = request.json.get('language')
    if lang_manager.set_language(lang_code):
        session['language'] = lang_code
        return jsonify({
            'success': True,
            'translations': lang_manager.translations[lang_code]
        })
    return jsonify({'success': False, 'error': 'Unsupported language'}), 400

@app.route('/api/get-translations')
def get_translations():
    """현재 언어의 번역 데이터를 반환합니다."""
    lang_code = session.get('language', lang_manager.get_current_language())
    return jsonify(lang_manager.translations[lang_code])

if __name__ == '__main__':
    # 시작할 때 Ollama 서버 자동 시작
    if ollama.is_installed() and not ollama.is_server_running():
        ollama.start_server()
    app.run(debug=True, port=5000) 