#!/bin/bash

# Ensure correct Python version
if ! command -v python3.9 &> /dev/null; then
    echo "Python 3.9 is required but not found"
    exit 1
fi

# Create and activate virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install/upgrade required packages
pip install --upgrade pip
pip install --upgrade pyinstaller
pip install -r requirements.txt

# Clean previous builds
rm -rf build dist

# Build the application
pyinstaller QuantAnalysis.spec

# Code signing for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Create app bundle
    mkdir -p "dist/QuantAnalysis.app/Contents/MacOS"
    cp -r dist/QuantAnalysis/* "dist/QuantAnalysis.app/Contents/MacOS/"
    
    # Sign the app bundle with entitlements
    codesign --force --deep --sign - --entitlements entitlements.plist --options runtime "dist/QuantAnalysis.app"
    
    # Verify signing
    codesign --verify --deep --strict "dist/QuantAnalysis.app"
fi

echo "Build completed!"

# Deactivate virtual environment
deactivate 