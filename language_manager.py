import json
import os
import locale
from typing import Dict, Optional

class LanguageManager:
    """다국어 지원을 위한 언어 관리 클래스"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'ja': '日本語',
            'fr': 'Français',
            'es': 'Español'
        }
        self.current_language = self._get_default_language()
        self.translations = self._load_translations()
        
    def _get_default_language(self) -> str:
        """시스템 기본 언어 설정을 가져옵니다."""
        try:
            # 시스템 로케일 가져오기
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in self.supported_languages:
                    return lang_code
        except Exception:
            pass
        return 'en'  # 기본값은 영어
        
    def _load_translations(self) -> Dict:
        """언어 파일들을 로드합니다."""
        translations = {}
        locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        
        for lang_code in self.supported_languages:
            file_path = os.path.join(locales_dir, f'{lang_code}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading language file {lang_code}: {str(e)}")
                translations[lang_code] = {}
                
        return translations
        
    def set_language(self, lang_code: str) -> bool:
        """언어를 설정합니다."""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            return True
        return False
        
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """번역된 텍스트를 가져옵니다."""
        try:
            # 키가 점(.)으로 구분된 경우 중첩된 딕셔너리에서 값을 찾습니다
            current_dict = self.translations[self.current_language]
            for part in key.split('.'):
                current_dict = current_dict[part]
            return current_dict
        except (KeyError, TypeError):
            # 현재 언어에서 찾을 수 없는 경우 영어로 시도
            if self.current_language != 'en':
                try:
                    current_dict = self.translations['en']
                    for part in key.split('.'):
                        current_dict = current_dict[part]
                    return current_dict
                except (KeyError, TypeError):
                    pass
            return default if default is not None else key
            
    def get_current_language(self) -> str:
        """현재 설정된 언어 코드를 반환합니다."""
        return self.current_language
        
    def get_language_name(self, lang_code: Optional[str] = None) -> str:
        """언어 코드에 해당하는 언어 이름을 반환합니다."""
        code = lang_code or self.current_language
        return self.supported_languages.get(code, 'Unknown') 