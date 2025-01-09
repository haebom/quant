import os
from typing import List, Optional
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class BinanceDataCollector:
    def __init__(self, symbols: List[str], api_key: str = None, api_secret: str = None, use_testnet: bool = False):
        """
        Binance 데이터 수집기 초기화
        :param symbols: 수집할 심볼 리스트
        :param api_key: Binance API Key
        :param api_secret: Binance Secret Key
        :param use_testnet: 테스트넷 사용 여부
        """
        try:
            # API 키 설정
            self.api_key = api_key or os.getenv('BINANCE_API_KEY')
            self.api_secret = api_secret or os.getenv('BINANCE_SECRET_KEY')
            
            if not self.api_key or not self.api_secret:
                raise ValueError("API 키가 설정되지 않았습니다.")
            
            # Binance 클라이언트 초기화
            self.client = Client(self.api_key, self.api_secret, testnet=use_testnet)
            
            # 심볼 목록 설정 및 검증
            self.symbols = symbols
            self._validate_symbols()
            
        except Exception as e:
            print(f"Binance 데이터 수집기 초기화 오류: {str(e)}")
            raise
            
    def _validate_symbols(self):
        """심볼 유효성 검사"""
        try:
            exchange_info = self.client.get_exchange_info()
            valid_symbols = {s['symbol'] for s in exchange_info['symbols']}
            
            for symbol in self.symbols:
                if symbol not in valid_symbols:
                    raise ValueError(f"유효하지 않은 심볼: {symbol}")
                    
        except BinanceAPIException as e:
            print(f"Binance API 오류: {str(e)}")
            raise
        except Exception as e:
            print(f"심볼 검증 오류: {str(e)}")
            raise
            
    def get_historical_data(self, symbol: str, interval: str = '1d', limit: int = 1000) -> Optional[pd.DataFrame]:
        """
        히스토리컬 데이터 수집
        :param symbol: 심볼
        :param interval: 데이터 간격
        :param limit: 데이터 개수
        :return: DataFrame 또는 None
        """
        try:
            # 유효한 인터벌 검사
            valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
            if interval not in valid_intervals:
                raise ValueError(f"유효하지 않은 인터벌입니다. 가능한 값: {', '.join(valid_intervals)}")
            
            # 데이터 수집
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # DataFrame 생성
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                             'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                                             'taker_buy_quote', 'ignored'])
            
            # 데이터 타입 변환
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            return df
            
        except BinanceAPIException as e:
            print(f"Binance API 오류: {str(e)}")
            return None
        except Exception as e:
            print(f"데이터 수집 오류: {str(e)}")
            return None 