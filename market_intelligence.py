from data_collector import BinanceDataCollector
from technical_analysis import TechnicalAnalysis
from position_analyzer import PositionAnalyzer
from typing import Dict, Optional, List
import pandas as pd

class MarketIntelligence:
    def __init__(self, symbols: List[str], api_key: str = None, api_secret: str = None, use_testnet: bool = False):
        """
        시장 분석 클래스 초기화
        :param symbols: 분석할 심볼 리스트
        :param api_key: Binance API Key
        :param api_secret: Binance Secret Key
        :param use_testnet: 테스트넷 사용 여부
        """
        try:
            self.collector = BinanceDataCollector(symbols, api_key, api_secret, use_testnet)
            self.valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
            self.ma_periods = [5, 10, 30, 60, 90, 120, 240, 360]  # 이동평균선 기간 설정
        except Exception as e:
            print(f"MarketIntelligence 초기화 오류: {str(e)}")
            raise
        
    def get_complete_analysis(self, symbol: str, interval: str = '1d') -> Optional[Dict]:
        """
        전체 시장 분석 수행
        :param symbol: 분석할 심볼
        :param interval: 데이터 간격
        :return: 분석 결과 딕셔너리
        """
        try:
            # 인터벌 유효성 검사
            if interval not in self.valid_intervals:
                raise ValueError(f"유효하지 않은 인터벌입니다. 가능한 값: {', '.join(self.valid_intervals)}")
            
            # 데이터 수집
            df = self.collector.get_historical_data(symbol, interval)
            if df is None or df.empty:
                raise ValueError(f"데이터 수집 실패: {symbol}")
            
            # 기술적 지표 추가
            ta = TechnicalAnalysis()
            
            # 이동평균선 추가
            df = ta.add_moving_averages(df, self.ma_periods)
            
            # 기타 지표 추가
            df = ta.add_rsi(df)
            df = ta.add_macd(df)
            df = ta.add_bollinger_bands(df)
            
            if df is None:
                raise ValueError("기술적 지표 계산 실패")
            
            # 포지션 분석
            position_analyzer = PositionAnalyzer(df)
            position_analyzer.find_support_resistance()
            position_analysis = position_analyzer.analyze_position()
            
            if position_analysis is None:
                raise ValueError("포지션 분석 실패")
            
            return {
                "기술적_분석": position_analysis,
                "데이터_시간": df.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
                "분석_시간": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"시장 분석 오류: {str(e)}")
            return None
            
    def get_supported_symbols(self) -> List[str]:
        """지원하는 심볼 목록 반환"""
        return self.collector.symbols 