import requests
import json
from typing import Dict

class AIAnalyzer:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.endpoint = "http://localhost:11434/api/generate"
        
    def analyze_market_condition(self, market_data: Dict) -> str:
        """AI 기반 시장 분석"""
        prompt = self._create_analysis_prompt(market_data)
        
        response = requests.post(
            self.endpoint,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()['response']
        return "AI 분석 실패"
    
    def _create_analysis_prompt(self, market_data: Dict) -> str:
        """분석 프롬프트 생성"""
        return f"""
        다음 시장 데이터를 기반으로 현재 시장 상황을 분석하고 트레이딩 전략을 제시해주세요:
        
        현재가: {market_data['현재가']}
        RSI: {market_data['기술적_지표']['RSI']}
        볼린저밴드: {market_data['기술적_지표']['볼린저밴드']}
        MACD: {market_data['기술적_지표']['MACD']}
        이동평균선: {market_data['기술적_지표']['이동평균선']}
        
        지지선: {market_data['지지선']}
        저항선: {market_data['저항선']}
        
        다음 사항을 포함해서 분석해주세요:
        1. 현재 시장 트렌드
        2. 주요 지지/저항 레벨
        3. 단기 및 중기 전망
        4. 롱/숏 포지션 진입 전략
        5. 리스크 관리 방안
        """ 