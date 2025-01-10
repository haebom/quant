import os
import sys
import certifi

def _setup_environment():
    if getattr(sys, 'frozen', False):
        # 실행 파일 내부의 경로 설정
        bundle_dir = sys._MEIPASS
        
        # Python 환경 설정
        os.environ['PYTHONHOME'] = bundle_dir
        os.environ['PYTHONPATH'] = bundle_dir
        
        # 인코딩 설정
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'
        
        # SSL 인증서 설정
        cert_file = os.path.join(bundle_dir, 'certifi', 'cacert.pem')
        if os.path.exists(cert_file):
            os.environ['SSL_CERT_FILE'] = cert_file
            os.environ['REQUESTS_CA_BUNDLE'] = cert_file
        else:
            os.environ['SSL_CERT_FILE'] = certifi.where()
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        # macOS 특정 설정
        os.environ['DYLD_LIBRARY_PATH'] = ''
        os.environ['DYLD_FRAMEWORK_PATH'] = ''

_setup_environment() 