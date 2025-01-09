import pandas as pd
import numpy as np
from typing import Optional, List

class TechnicalAnalysis:
    @staticmethod
    def add_moving_averages(df: pd.DataFrame, periods: List[int], column: str = 'close') -> Optional[pd.DataFrame]:
        """여러 기간의 이동평균선 계산"""
        try:
            if column not in df.columns:
                raise ValueError(f"컬럼 '{column}'이 데이터프레임에 없습니다.")
            
            for period in periods:
                if period <= 0:
                    raise ValueError("기간은 0보다 커야 합니다.")
                df[f'MA_{period}'] = df[column].rolling(window=period).mean()
            
            return df
        except Exception as e:
            print(f"이동평균 계산 오류: {str(e)}")
            return None
    
    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> Optional[pd.DataFrame]:
        """RSI 지표 계산"""
        try:
            if column not in df.columns:
                raise ValueError(f"컬럼 '{column}'이 데이터프레임에 없습니다.")
            if period <= 0:
                raise ValueError("기간은 0보다 커야 합니다.")
                
            delta = df[column].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
            return df
        except Exception as e:
            print(f"RSI 계산 오류: {str(e)}")
            return None
    
    @staticmethod
    def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9,
                 column: str = 'close') -> Optional[pd.DataFrame]:
        """MACD 지표 계산"""
        try:
            if column not in df.columns:
                raise ValueError(f"컬럼 '{column}'이 데이터프레임에 없습니다.")
            if fast <= 0 or slow <= 0 or signal <= 0:
                raise ValueError("모든 기간은 0보다 커야 합니다.")
            if fast >= slow:
                raise ValueError("slow 기간은 fast 기간보다 커야 합니다.")
                
            exp1 = df[column].ewm(span=fast, adjust=False).mean()
            exp2 = df[column].ewm(span=slow, adjust=False).mean()
            
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            return df
        except Exception as e:
            print(f"MACD 계산 오류: {str(e)}")
            return None
    
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std: int = 2,
                           column: str = 'close') -> Optional[pd.DataFrame]:
        """볼린저 밴드 계산"""
        try:
            if column not in df.columns:
                raise ValueError(f"컬럼 '{column}'이 데이터프레임에 없습니다.")
            if period <= 0:
                raise ValueError("기간은 0보다 커야 합니다.")
            if std <= 0:
                raise ValueError("표준편차 승수는 0보다 커야 합니다.")
                
            df[f'BB_Middle_{period}'] = df[column].rolling(window=period).mean()
            std_dev = df[column].rolling(window=period).std()
            df[f'BB_Upper_{period}'] = df[f'BB_Middle_{period}'] + (std_dev * std)
            df[f'BB_Lower_{period}'] = df[f'BB_Middle_{period}'] - (std_dev * std)
            return df
        except Exception as e:
            print(f"볼린저 밴드 계산 오류: {str(e)}")
            return None 