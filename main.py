from market_intelligence import MarketIntelligence
from quant_models import QuantModels
import json

def main():
    try:
        # 분석하고 싶은 심볼 리스트
        symbols = ['BTCUSDT']
        
        # MarketIntelligence 인스턴스 생성
        mi = MarketIntelligence(symbols)
        
        # Quant 모델 인스턴스 생성
        qm = QuantModels()
        
        # BTCUSDT에 대한 분석 실행
        analysis = mi.get_complete_analysis('BTCUSDT')
        
        if analysis is None:
            print("분석 결과를 가져오는데 실패했습니다.")
            return
            
        # 기술적 분석 결과 출력
        print("\n=== 기술적 분석 ===")
        if '기술적_분석' in analysis:
            print(json.dumps(analysis['기술적_분석'], indent=2, ensure_ascii=False))
        else:
            print("기술적 분석 결과가 없습니다.")
        
        # Quant 모델 분석 실행
        print("\n=== Quant 모델 분석 ===")
        
        # 평균 회귀 전략 실행
        mean_rev_result = qm.run_model('mean_reversion', analysis['raw_data'])
        print("\n- 평균 회귀 전략 신호:")
        print(json.dumps(mean_rev_result['signals'], indent=2, ensure_ascii=False))
        
        # 모멘텀 전략 실행
        momentum_result = qm.run_model('momentum', analysis['raw_data'])
        print("\n- 모멘텀 전략 신호:")
        print(json.dumps(momentum_result['signals'], indent=2, ensure_ascii=False))
        
        # 팩터 모델 실행
        factor_result = qm.run_model('factor_model', analysis['raw_data'])
        print("\n- 팩터 모델 분석:")
        print(json.dumps(factor_result['correlation'], indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 