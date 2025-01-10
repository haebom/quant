import os
import sys
import site
import certifi

def _setup_environment():
    if getattr(sys, 'frozen', False):
        # 실행 파일 내부의 경로 설정
        bundle_dir = sys._MEIPASS
        
        # Python 라이브러리 경로 설정
        os.environ['PYTHONPATH'] = bundle_dir
        
        # SSL 인증서 경로 설정
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        # 환경 변수 설정
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        
        # 라이브러리 검색 경로 설정
        os.environ['DYLD_LIBRARY_PATH'] = bundle_dir
        os.environ['DYLD_FRAMEWORK_PATH'] = bundle_dir
        
        # site-packages 경로 추가
        site.addsitedir(bundle_dir)
        
        # Python 프레임워크 경로 설정
        framework_path = os.path.join(bundle_dir, 'Python.framework', 'Versions', '3.9')
        if os.path.exists(framework_path):
            os.environ['PYTHONHOME'] = framework_path

_setup_environment() 