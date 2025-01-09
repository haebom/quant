import sys
import os
import webbrowser
from threading import Timer
from server import app

def open_browser():
    """기본 브라우저에서 애플리케이션을 엽니다."""
    webbrowser.open('http://localhost:5000')

def resource_path(relative_path):
    """PyInstaller를 위한 리소스 경로 처리"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    """메인 실행 함수"""
    print("Crypto Trading Assistant 시작 중...")
    print("잠시만 기다려주세요...")
    
    # 3초 후 브라우저 자동 실행
    Timer(3, open_browser).start()
    
    # Flask 앱 실행
    app.run(port=5000)

if __name__ == '__main__':
    main() 