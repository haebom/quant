from data_collector import BinanceDataCollector
from technical_analysis import TechnicalAnalysis
import pandas as pd

class MarketAnalyzer:
    def __init__(self, symbols):
        self.collector = BinanceDataCollector(symbols)
        self.ta = TechnicalAnalysis()
        self.analysis_data = {}
        
    def analyze_market(self, symbol, interval='1d', limit=1000):
        # 히스토리컬 데이터 수집
        df = self.collector.get_historical_data(symbol, interval, limit)
        
        # 기술적 지표 추가
        df = self.ta.add_moving_average(df, 20)  # 20일 이동평균
        df = self.ta.add_moving_average(df, 50)  # 50일 이동평균
        df = self.ta.add_rsi(df)                 # RSI
        df = self.ta.add_macd(df)                # MACD
        df = self.ta.add_bollinger_bands(df)     # 볼린저 밴드
        
        self.analysis_data[symbol] = df
        return df
    
    def get_market_summary(self, symbol):
        """현재 시장 상황 요약"""
        if symbol not in self.analysis_data:
            return "먼저 analyze_market을 실행해주세요."
            
        df = self.analysis_data[symbol]
        latest = df.iloc[-1]
        
        summary = {
            "현재가": latest['close'],
            "RSI": latest['RSI_14'],
            "MACD": latest['MACD'],
            "볼린저밴드": {
                "상단": latest['BB_Upper_20'],
                "중간": latest['BB_Middle_20'],
                "하단": latest['BB_Lower_20']
            },
            "이동평균선": {
                "MA20": latest['MA_20'],
                "MA50": latest['MA_50']
            }
        }
        
        return summary 