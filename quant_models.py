import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

class QuantModels:
    def __init__(self):
        self.models = {
            'mean_reversion': self.mean_reversion_strategy,
            'momentum': self.momentum_strategy,
            'factor_model': self.factor_model,
            'stat_arbitrage': self.statistical_arbitrage
        }
    
    def mean_reversion_strategy(self, data, window=20, std_dev=2):
        """
        평균 회귀 전략
        - window: 이동평균 기간
        - std_dev: 표준편차 배수
        """
        df = pd.DataFrame(data)
        df['SMA'] = df['close'].rolling(window=window).mean()
        df['stddev'] = df['close'].rolling(window=window).std()
        df['upper_band'] = df['SMA'] + (df['stddev'] * std_dev)
        df['lower_band'] = df['SMA'] - (df['stddev'] * std_dev)
        
        return {
            'signals': {
                'buy': df['close'] < df['lower_band'],
                'sell': df['close'] > df['upper_band']
            },
            'metrics': df[['SMA', 'upper_band', 'lower_band']].to_dict()
        }
    
    def momentum_strategy(self, data, lookback=14):
        """
        모멘텀 전략
        - lookback: 모멘텀 계산 기간
        """
        df = pd.DataFrame(data)
        df['momentum'] = df['close'].pct_change(lookback)
        df['signal'] = np.where(df['momentum'] > 0, 1, -1)
        
        return {
            'signals': {
                'buy': df['momentum'] > 0,
                'sell': df['momentum'] < 0
            },
            'metrics': {
                'momentum': df['momentum'].to_dict()
            }
        }
    
    def factor_model(self, data, factors=['volume', 'volatility']):
        """
        팩터 모델
        - factors: 사용할 팩터 리스트
        """
        df = pd.DataFrame(data)
        factor_data = {}
        
        # 기본 팩터 계산
        if 'volume' in factors:
            factor_data['volume'] = df['volume'].rolling(window=5).mean()
        if 'volatility' in factors:
            factor_data['volatility'] = df['close'].rolling(window=20).std()
            
        return {
            'factors': factor_data,
            'correlation': {f: stats.pearsonr(df['close'], factor_data[f])[0] 
                          for f in factor_data.keys()}
        }
    
    def statistical_arbitrage(self, data1, data2, window=30):
        """
        통계적 차익거래
        - window: 상관관계 계산 기간
        """
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        # 가격 스프레드 계산
        spread = df1['close'] - df2['close']
        spread_mean = spread.rolling(window=window).mean()
        spread_std = spread.rolling(window=window).std()
        
        z_score = (spread - spread_mean) / spread_std
        
        return {
            'signals': {
                'long_short': z_score < -2,  # pair1 매수, pair2 매도
                'short_long': z_score > 2    # pair1 매도, pair2 매수
            },
            'metrics': {
                'z_score': z_score.to_dict(),
                'spread': spread.to_dict()
            }
        }
    
    def run_model(self, model_name, data, **params):
        """
        선택한 모델 실행
        """
        if model_name not in self.models:
            raise ValueError(f"지원하지 않는 모델입니다: {model_name}")
            
        return self.models[model_name](data, **params) 