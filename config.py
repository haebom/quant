import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'GPjAQsuHo2nrpUjCyvgTT8iy4fXBKunaiB7ZWstZ6cq4PCQmzsetoJ7Gd0HHyZoX')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'GPjAQsuHo2nrpUjCyvgTT8iy4fXBKunaiB7ZWstZ6cq4PCQmzsetoJ7Gd0HHyZoX')

# Binance Endpoints (메인넷)
REST_ENDPOINT = "https://api.binance.com"
WEBSOCKET_ENDPOINT = "wss://stream.binance.com:9443"

# Binance Endpoints (테스트넷 - 필요시 주석 해제)
# REST_ENDPOINT = "https://testnet.binance.vision"
# WEBSOCKET_ENDPOINT = "wss://testnet.binance.vision/ws"

# Ollama Configuration
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "llama2"

# Trading Parameters
DEFAULT_TIMEFRAME = '1h'
DEFAULT_LIMIT = 100
SUPPORTED_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

# Technical Analysis Parameters
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2 