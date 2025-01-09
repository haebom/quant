import os
import sys
import subprocess
import requests
import time
import platform
from pathlib import Path
import webbrowser

class OllamaManager:
    def __init__(self):
        """Ollama 관리자 초기화"""
        self.system = platform.system().lower()
        self.ollama_path = self._get_ollama_path()
        self.server_process = None
        
    def _get_ollama_path(self) -> str:
        """시스템에 맞는 Ollama 실행 파일 경로 반환"""
        if self.system == 'darwin':  # macOS
            return '/usr/local/bin/ollama'
        elif self.system == 'windows':
            return os.path.expanduser('~\\AppData\\Local\\Programs\\Ollama\\ollama.exe')
        else:  # Linux
            return '/usr/local/bin/ollama'
            
    def is_installed(self) -> bool:
        """Ollama가 설치되어 있는지 확인"""
        return os.path.exists(self.ollama_path)
        
    def install_ollama(self):
        """Ollama 설치"""
        if self.system == 'darwin':
            webbrowser.open('https://ollama.ai/download/mac')
        elif self.system == 'windows':
            webbrowser.open('https://ollama.ai/download/windows')
        else:
            webbrowser.open('https://ollama.ai/download/linux')
            
    def is_server_running(self) -> bool:
        """Ollama 서버가 실행 중인지 확인"""
        try:
            response = requests.get('http://localhost:11434/api/tags')
            return response.status_code == 200
        except:
            return False
            
    def start_server(self):
        """Ollama 서버 시작"""
        if not self.is_server_running():
            if self.system == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.server_process = subprocess.Popen(
                    [self.ollama_path, 'serve'],
                    startupinfo=startupinfo
                )
            else:
                self.server_process = subprocess.Popen(
                    [self.ollama_path, 'serve'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            # 서버가 시작될 때까지 대기
            for _ in range(30):  # 30초 타임아웃
                if self.is_server_running():
                    break
                time.sleep(1)
                
    def stop_server(self):
        """Ollama 서버 중지"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            
    def get_installed_models(self) -> list:
        """설치된 모델 목록 반환"""
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                return [model['name'] for model in response.json()['models']]
            return []
        except:
            return []
            
    def install_model(self, model_name: str):
        """모델 설치"""
        try:
            subprocess.run([self.ollama_path, 'pull', model_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def is_model_installed(self, model_name: str) -> bool:
        """특정 모델이 설치되어 있는지 확인"""
        return model_name in self.get_installed_models()
        
    def get_model_info(self, model_name: str) -> dict:
        """모델 정보 반환"""
        try:
            response = requests.get(f'http://localhost:11434/api/show?name={model_name}')
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {} 