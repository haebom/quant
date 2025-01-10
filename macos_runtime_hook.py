import os
import sys

# SSL 인증서 경로 설정
if sys.platform == 'darwin':
    if getattr(sys, 'frozen', False):
        # 실행 파일 내부의 인증서 경로
        bundle_dir = sys._MEIPASS
        os.environ['SSL_CERT_FILE'] = os.path.join(bundle_dir, 'certifi', 'cacert.pem')
        
# 환경 변수 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 라이브러리 검색 경로 설정
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    os.environ['DYLD_LIBRARY_PATH'] = bundle_dir
    os.environ['DYLD_FRAMEWORK_PATH'] = bundle_dir 