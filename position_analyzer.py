from technical_analysis import TechnicalAnalysis
import pandas as pd
import numpy as np
from typing import Dict, List
import requests

class PositionAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.support_levels = []
        self.resistance_levels = []
        
    def find_support_resistance(self, window: int = 20, threshold: float = 0.02):
        """지지/저항 레벨 찾기"""
        df = self.df.copy()
        
        # 피봇 포인트 찾기
        for i in range(window, len(df) - window):
            if self._is_support(df, i, window):
                self.support_levels.append(df['low'].iloc[i])
            if self._is_resistance(df, i, window):
                self.resistance_levels.append(df['high'].iloc[i])
        
        # 비슷한 레벨 통합
        self.support_levels = self._consolidate_levels(self.support_levels, threshold)
        self.resistance_levels = self._consolidate_levels(self.resistance_levels, threshold)
        
    def _is_support(self, df: pd.DataFrame, i: int, window: int) -> bool:
        """지지선 조건 확인"""
        return all(df['low'].iloc[i] <= df['low'].iloc[j] for j in range(i-window, i+window+1))
    
    def _is_resistance(self, df: pd.DataFrame, i: int, window: int) -> bool:
        """저항선 조건 확인"""
        return all(df['high'].iloc[i] >= df['high'].iloc[j] for j in range(i-window, i+window+1))
    
    def _consolidate_levels(self, levels: List[float], threshold: float) -> List[float]:
        """비슷한 가격대의 레벨 통합"""
        levels = sorted(levels)
        consolidated = []
        i = 0
        while i < len(levels):
            current = levels[i]
            while i + 1 < len(levels) and abs(levels[i+1] - current) / current < threshold:
                i += 1
            consolidated.append(current)
            i += 1
        return consolidated
    
    def analyze_position(self) -> Dict:
        """포지션 분석"""
        try:
            current_price = float(self.df['close'].iloc[-1])
            
            # RSI 기반 과매수/과매도 확인
            rsi = float(self.df['RSI_14'].iloc[-1])
            rsi_signal = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"
            
            # 볼린저 밴드 위치 확인
            bb_position = self._check_bb_position(current_price)
            
            # MACD 시그널 확인
            macd_signal = self._check_macd_signal()
            
            # 이동평균선 크로스 확인
            ma_signal = self._check_ma_cross()
            
            # 지지/저항 레벨 변환
            support_levels = [float(level) for level in self.support_levels[-3:]] if self.support_levels else []
            resistance_levels = [float(level) for level in self.resistance_levels[-3:]] if self.resistance_levels else []
            
            return {
                "현재가": current_price,
                "기술적_지표": {
                    "RSI": {
                        "값": float(rsi),
                        "신호": rsi_signal
                    },
                    "볼린저밴드": bb_position,
                    "MACD": macd_signal,
                    "이동평균선": ma_signal
                },
                "지지선": support_levels,
                "저항선": resistance_levels,
                "포지션_제안": self._generate_position_suggestion()
            }
        except Exception as e:
            print(f"포지션 분석 오류: {str(e)}")
            return None
            
    def _check_bb_position(self, price: float) -> Dict:
        """볼린저 밴드 상의 위치 확인"""
        try:
            latest = self.df.iloc[-1]
            return {
                "위치": "상단초과" if price > latest['BB_Upper_20'] else
                       "하단미만" if price < latest['BB_Lower_20'] else "밴드내",
                "밴드폭": float((latest['BB_Upper_20'] - latest['BB_Lower_20']) / latest['BB_Middle_20'])
            }
        except Exception as e:
            print(f"볼린저 밴드 위치 확인 오류: {str(e)}")
            return {"위치": "확인불가", "밴드폭": 0.0}
    
    def _check_macd_signal(self) -> str:
        """MACD 신호 확인"""
        if self.df['MACD'].iloc[-1] > self.df['MACD_Signal'].iloc[-1] and \
           self.df['MACD'].iloc[-2] <= self.df['MACD_Signal'].iloc[-2]:
            return "골든크로스"
        elif self.df['MACD'].iloc[-1] < self.df['MACD_Signal'].iloc[-1] and \
             self.df['MACD'].iloc[-2] >= self.df['MACD_Signal'].iloc[-2]:
            return "데드크로스"
        return "중립"
    
    def _check_ma_cross(self) -> str:
        """이동평균선 크로스 확인"""
        if self.df['MA_20'].iloc[-1] > self.df['MA_50'].iloc[-1] and \
           self.df['MA_20'].iloc[-2] <= self.df['MA_50'].iloc[-2]:
            return "골든크로스"
        elif self.df['MA_20'].iloc[-1] < self.df['MA_50'].iloc[-1] and \
             self.df['MA_20'].iloc[-2] >= self.df['MA_50'].iloc[-2]:
            return "데드크로스"
        return "중립"

    def _generate_position_suggestion(self) -> Dict:
        """포지션 진입/청산 제안 생성"""
        try:
            current_price = float(self.df['close'].iloc[-1])
            rsi = float(self.df['RSI_14'].iloc[-1])
            macd_signal = self._check_macd_signal()
            ma_signal = self._check_ma_cross()
            bb_position = self._check_bb_position(current_price)

            # 매수 신호 조건
            buy_signals = [
                rsi < 30,  # 과매도
                macd_signal == "골든크로스",
                ma_signal == "골든크로스",
                bb_position["위치"] == "하단미만"
            ]

            # 매도 신호 조건
            sell_signals = [
                rsi > 70,  # 과매수
                macd_signal == "데드크로스",
                ma_signal == "데드크로스",
                bb_position["위치"] == "상단초과"
            ]

            # 신호 강도 계산
            buy_strength = int(sum(buy_signals))
            sell_strength = int(sum(sell_signals))

            # 포지션 제안 생성
            if buy_strength > sell_strength and buy_strength >= 2:
                position = "매수"
                strength = buy_strength
            elif sell_strength > buy_strength and sell_strength >= 2:
                position = "매도"
                strength = sell_strength
            else:
                position = "관망"
                strength = 0

            return {
                "포지션": position,
                "신호강도": int(strength),
                "매수신호수": int(buy_strength),
                "매도신호수": int(sell_strength)
            }
        except Exception as e:
            print(f"포지션 제안 생성 오류: {str(e)}")
            return {
                "포지션": "오류",
                "신호강도": 0,
                "매수신호수": 0,
                "매도신호수": 0
            } 