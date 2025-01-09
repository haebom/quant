#!/bin/bash

# Windows용 빌드 실행
wine python build_config.py

# 빌드된 파일 권한 설정
chmod -R 777 dist/ 