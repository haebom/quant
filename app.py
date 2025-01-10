from flask import Flask, render_template, request, jsonify, send_file
from market_intelligence import MarketIntelligence
from quant_models import QuantModels
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import jinja2

app = Flask(__name__)

# 결과 저장 디렉토리 생성
BACKTEST_DIR = "backtest_results"
REPORT_DIR = "reports"
for directory in [BACKTEST_DIR, REPORT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 다국어 설정
TRANSLATIONS = {
    'ko': {
        'performance_metrics': '성과 지표',
        'total_return': '총 수익률',
        'annual_return': '연간 수익률',
        'sharpe_ratio': '샤프 비율',
        'max_drawdown': '최대 낙폭',
        'win_rate': '승률',
        'profit_factor': '수익 팩터',
        'avg_profit_loss': '평균 손익',
        'avg_win': '평균 수익',
        'avg_loss': '평균 손실',
        'risk_metrics': '리스크 지표',
        'volatility': '변동성',
        'sortino_ratio': '소티노 비율',
        'calmar_ratio': '칼마 비율',
        'trade_analysis': '거래 분석',
        'total_trades': '총 거래 수',
        'winning_trades': '수익 거래',
        'losing_trades': '손실 거래',
        'avg_holding': '평균 보유 기간',
        'report_title': '백테스트 분석 리포트',
        'model_info': '모델 정보',
        'symbol_info': '심볼 정보',
        'date_range': '분석 기간',
        'parameters': '파라미터',
        'legal_disclaimer': '법적 고지사항',
        'compliance_storage': '서비스 제공자는 생성된 조사분석자료는 {date} 현재 위 조사분석자료에 언급된 종목의 내용을 타서버에 별도 저장하거나 취합하지 않습니다.',
        'compliance_independence': '본 조사분석자료에는 외부의 부당한 압력이나 간섭 없이 정량적 수치를 기반으로한 기술적 분석과 생성형 모델의 의견이 정확하게 반영되었음을 확인합니다.',
        'compliance_copyright': '본 조사분석자료는 당사의 저작물로서 모든 저작권은 사용자에게 있습니다. 다만, 출처 및 워터마크만 밝혀주세요.',
        'compliance_disclaimer': '본 조사분석자료에 수록된 내용은 그 정확성이나 완전성을 보장할 수 없습니다. 따라서 어떠한 경우에도 본 자료는 고객의 주식투자의 결과에 대한 법적 책임소재에 대한 증빙자료로 사용될 수 없습니다.',
        'compliance_confidentiality': '본 조사분석자료는 기관투자가 등 제3자에게 사전 제공된 사실이 없습니다. 오로지 당신의 개인 컴퓨터에 저장됩니다.',
        'watermark_text': '© {year} QuantAnalysis. 생성일: {date}'
    },
    'en': {
        'performance_metrics': 'Performance Metrics',
        'total_return': 'Total Return',
        'annual_return': 'Annual Return',
        'sharpe_ratio': 'Sharpe Ratio',
        'max_drawdown': 'Maximum Drawdown',
        'win_rate': 'Win Rate',
        'profit_factor': 'Profit Factor',
        'avg_profit_loss': 'Average P/L',
        'avg_win': 'Average Win',
        'avg_loss': 'Average Loss',
        'risk_metrics': 'Risk Metrics',
        'volatility': 'Volatility',
        'sortino_ratio': 'Sortino Ratio',
        'calmar_ratio': 'Calmar Ratio',
        'trade_analysis': 'Trade Analysis',
        'total_trades': 'Total Trades',
        'winning_trades': 'Winning Trades',
        'losing_trades': 'Losing Trades',
        'avg_holding': 'Average Holding Period',
        'report_title': 'Backtest Analysis Report',
        'model_info': 'Model Information',
        'symbol_info': 'Symbol Information',
        'date_range': 'Date Range',
        'parameters': 'Parameters',
        'legal_disclaimer': 'Legal Disclaimer',
        'compliance_storage': 'As of {date}, the service provider does not store or aggregate the content of the mentioned securities in this research analysis material on any external servers.',
        'compliance_independence': 'This research analysis material accurately reflects technical analysis based on quantitative figures and opinions of generative models without any external pressure or interference.',
        'compliance_copyright': 'This research analysis material is our work and all copyrights belong to the user. However, please acknowledge the source and watermark.',
        'compliance_disclaimer': 'The content of this research analysis material cannot guarantee its accuracy or completeness. Therefore, this material cannot be used as evidence for legal liability regarding the results of customer stock investments under any circumstances.',
        'compliance_confidentiality': 'This research analysis material has not been provided to third parties such as institutional investors in advance. It is stored only on your personal computer.',
        'watermark_text': '© {year} QuantAnalysis. Generated on: {date}'
    }
}

def calculate_metrics(data, trades):
    """성과 지표 계산"""
    returns = pd.Series(data['returns'])
    
    metrics = {
        'total_return': (returns + 1).prod() - 1,
        'annual_return': ((returns + 1).prod() ** (252/len(returns))) - 1,
        'volatility': returns.std() * np.sqrt(252),
        'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252),
        'max_drawdown': (returns + 1).cumprod().div((returns + 1).cumprod().cummax()) - 1,
        'win_rate': len(trades[trades['profit'] > 0]) / len(trades),
        'profit_factor': abs(trades[trades['profit'] > 0]['profit'].sum() / trades[trades['profit'] < 0]['profit'].sum()),
        'avg_profit_loss': trades['profit'].mean(),
        'avg_win': trades[trades['profit'] > 0]['profit'].mean(),
        'avg_loss': trades[trades['profit'] < 0]['profit'].mean(),
        'sortino_ratio': returns.mean() / returns[returns < 0].std() * np.sqrt(252),
        'calmar_ratio': ((returns + 1).prod() ** (252/len(returns)) - 1) / abs((returns + 1).cumprod().div((returns + 1).cumprod().cummax()) - 1).min(),
        'total_trades': len(trades),
        'winning_trades': len(trades[trades['profit'] > 0]),
        'losing_trades': len(trades[trades['profit'] < 0]),
        'avg_holding': trades['holding_period'].mean()
    }
    
    return metrics

def generate_report(backtest_data, lang='ko'):
    """분석 리포트 생성"""
    translations = TRANSLATIONS[lang]
    report_date = datetime.now().strftime('%Y년 %m월 %d일') if lang == 'ko' else datetime.now().strftime('%B %d, %Y')
    
    # HTML 템플릿 렌더링
    template = jinja2.Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ translations.report_title }}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    position: relative;
                }
                .metric-card { 
                    margin: 20px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: #fff;
                }
                .chart { 
                    width: 100%;
                    height: 400px;
                    margin: 20px 0;
                }
                .metric-value {
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .metric-label {
                    color: #7f8c8d;
                }
                .compliance-section {
                    margin-top: 40px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    font-size: 0.9em;
                }
                .compliance-section p {
                    margin-bottom: 10px;
                    color: #666;
                }
                .watermark {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    color: #999;
                    font-size: 0.8em;
                    opacity: 0.7;
                }
                @media print {
                    .watermark {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4">{{ translations.report_title }}</h1>
                
                <div class="metric-card">
                    <h2>{{ translations.model_info }}</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>모델:</strong> {{ backtest_data.model }}</p>
                            <p><strong>심볼:</strong> {{ backtest_data.symbol }}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>{{ translations.parameters }}:</strong></p>
                            <pre>{{ backtest_data.params | tojson(indent=2) }}</pre>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <h2>{{ translations.performance_metrics }}</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.total_return }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.total_return * 100) }}%</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.annual_return }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.annual_return * 100) }}%</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.sharpe_ratio }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.sharpe_ratio) }}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.win_rate }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.win_rate * 100) }}%</p>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <h2>{{ translations.risk_metrics }}</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.max_drawdown }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.max_drawdown.min() * 100) }}%</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.volatility }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.volatility * 100) }}%</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.sortino_ratio }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.sortino_ratio) }}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.calmar_ratio }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.calmar_ratio) }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <h2>{{ translations.trade_analysis }}</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.total_trades }}</p>
                            <p class="metric-value">{{ metrics.total_trades }}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.winning_trades }}</p>
                            <p class="metric-value">{{ metrics.winning_trades }}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.losing_trades }}</p>
                            <p class="metric-value">{{ metrics.losing_trades }}</p>
                        </div>
                        <div class="col-md-3">
                            <p class="metric-label">{{ translations.avg_profit_loss }}</p>
                            <p class="metric-value">{{ "%.2f"|format(metrics.avg_profit_loss * 100) }}%</p>
                        </div>
                    </div>
                </div>
                
                <div class="chart" id="performanceChart"></div>
                <div class="chart" id="drawdownChart"></div>
                <div class="chart" id="tradesChart"></div>
                
                <div class="compliance-section">
                    <h3>{{ translations.legal_disclaimer }}</h3>
                    <p>{{ translations.compliance_storage.format(date=report_date) }}</p>
                    <p>{{ translations.compliance_independence }}</p>
                    <p>{{ translations.compliance_copyright }}</p>
                    <p>{{ translations.compliance_disclaimer }}</p>
                    <p>{{ translations.compliance_confidentiality }}</p>
                </div>
                
                <div class="watermark">
                    {{ translations.watermark_text.format(year=current_year, date=report_date) }}
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    ''')
    
    # 현재 연도 가져오기
    current_year = datetime.now().year
    
    # 메트릭스 계산
    metrics = calculate_metrics(backtest_data['result']['data'], pd.DataFrame(backtest_data['result']['trades']))
    
    html = template.render(
        translations=translations,
        backtest_data=backtest_data,
        metrics=metrics,
        report_date=report_date,
        current_year=current_year
    )
    
    # HTML 파일 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{backtest_data['symbol']}_{backtest_data['model']}_{timestamp}"
    html_path = os.path.join(REPORT_DIR, f"{filename}.html")
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

@app.route('/api/backtest/report', methods=['POST'])
def create_report():
    try:
        data = request.json
        filename = data.get('filename')
        lang = data.get('lang', 'ko')
        
        if not filename:
            return jsonify({'error': '파일을 선택해주세요'})
            
        filepath = os.path.join(BACKTEST_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '파일을 찾을 수 없습니다'})
            
        with open(filepath, 'r') as f:
            backtest_data = json.load(f)
            
        report_filename = generate_report(backtest_data, lang)
        
        return jsonify({
            'success': True,
            'html_report': f"{report_filename}.html"
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/reports/<filename>')
def get_report(filename):
    return send_file(os.path.join(REPORT_DIR, filename))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/technical-analysis')
def technical_analysis():
    return render_template('technical_analysis.html')

@app.route('/quant-models')
def quant_models():
    return render_template('quant_models.html')

@app.route('/backtest')
def backtest():
    return render_template('backtest.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    
    mi = MarketIntelligence([symbol])
    analysis = mi.get_complete_analysis(symbol)
    
    if analysis is None:
        return jsonify({'error': '분석 실패'})
    
    return jsonify(analysis)

@app.route('/api/quant-analysis', methods=['POST'])
def quant_analysis():
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    model_name = data.get('model', 'mean_reversion')
    params = data.get('params', {})
    
    mi = MarketIntelligence([symbol])
    qm = QuantModels()
    
    analysis = mi.get_complete_analysis(symbol)
    if analysis is None:
        return jsonify({'error': '데이터 가져오기 실패'})
    
    try:
        result = qm.run_model(model_name, analysis['raw_data'], **params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    model_name = data.get('model', 'mean_reversion')
    params = data.get('params', {})
    
    # 백테스팅 실행
    mi = MarketIntelligence([symbol])
    qm = QuantModels()
    
    analysis = mi.get_complete_analysis(symbol)
    if analysis is None:
        return jsonify({'error': '데이터 가져오기 실패'})
    
    try:
        result = qm.run_model(model_name, analysis['raw_data'], **params)
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_{model_name}_{timestamp}.json"
        filepath = os.path.join(BACKTEST_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'symbol': symbol,
                'model': model_name,
                'params': params,
                'result': result,
                'timestamp': timestamp
            }, f, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/backtest/list', methods=['GET'])
def list_backtests():
    try:
        results = []
        for filename in os.listdir(BACKTEST_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(BACKTEST_DIR, filename), 'r') as f:
                    data = json.load(f)
                    results.append({
                        'filename': filename,
                        'symbol': data['symbol'],
                        'model': data['model'],
                        'params': data['params'],
                        'timestamp': data.get('timestamp', '')
                    })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/backtest/compare', methods=['POST'])
def compare_backtests():
    try:
        data = request.json
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': '비교할 백테스트를 선택해주세요'})
            
        results = []
        for filename in filenames:
            filepath = os.path.join(BACKTEST_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    backtest_data = json.load(f)
                    results.append({
                        'filename': filename,
                        'symbol': backtest_data['symbol'],
                        'model': backtest_data['model'],
                        'params': backtest_data['params'],
                        'result': backtest_data['result'],
                        'timestamp': backtest_data.get('timestamp', '')
                    })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    try:
        import watchdog
        debug_mode = True
    except ImportError:
        debug_mode = False
    
    app.run(host='0.0.0.0', port=5000, debug=debug_mode) 