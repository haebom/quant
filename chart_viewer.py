from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chart.html')

@app.route('/data')
def get_data():
    # MarketIntelligence에서 데이터 가져오기
    from market_intelligence import MarketIntelligence
    mi = MarketIntelligence(['BTCUSDT'])
    df = mi.collector.get_historical_data('BTCUSDT')
    
    # Lightweight Charts 포맷으로 변환
    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'time': row['timestamp'].strftime('%Y-%m-%d'),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close'])
        })
    
    return json.dumps(chart_data)

if __name__ == '__main__':
    app.run(debug=True) 