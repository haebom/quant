import requests
import json
from datetime import datetime

def test_binance_api():
    """Binance API 연결 테스트"""
    
    # 1. 기본 엔드포인트 테스트 (메인넷)
    print("\n=== Binance 메인넷 테스트 ===")
    try:
        response = requests.get("https://api.binance.com/api/v3/ping")
        print(f"서버 연결 상태: {'성공' if response.status_code == 200 else '실패'}")
    except Exception as e:
        print(f"메인넷 연결 오류: {str(e)}")

    # 2. 테스트넷 테스트
    print("\n=== Binance 테스트넷 테스트 ===")
    try:
        response = requests.get("https://testnet.binance.vision/api/v3/ping")
        print(f"테스트넷 연결 상태: {'성공' if response.status_code == 200 else '실패'}")
    except Exception as e:
        print(f"테스트넷 연결 오류: {str(e)}")

    # 3. BTCUSDT 시세 데이터 테스트 (메인넷)
    print("\n=== BTCUSDT 시세 데이터 테스트 ===")
    try:
        params = {
            'symbol': 'BTCUSDT',
            'interval': '1h',
            'limit': 10
        }
        response = requests.get("https://api.binance.com/api/v3/klines", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"데이터 수신 성공: {len(data)} 개의 캔들 데이터")
            
            # 최근 캔들 정보 출력
            latest = data[-1]
            print("\n최근 캔들 정보:")
            print(f"시간: {datetime.fromtimestamp(latest[0]/1000)}")
            print(f"시가: {latest[1]}")
            print(f"고가: {latest[2]}")
            print(f"저가: {latest[3]}")
            print(f"종가: {latest[4]}")
            print(f"거래량: {latest[5]}")
        else:
            print(f"데이터 수신 실패: {response.text}")
    except Exception as e:
        print(f"시세 데이터 조회 오류: {str(e)}")

if __name__ == "__main__":
    test_binance_api() 