#!/bin/bash

echo "Building macOS version..."
python build_config.py

echo "Creating DMG for macOS..."
create-dmg \
  --volname "QuantAnalysis" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "QuantAnalysis.app" 200 190 \
  --hide-extension "QuantAnalysis.app" \
  --app-drop-link 600 185 \
  "QuantAnalysis.dmg" \
  "dist/QuantAnalysis.app"

echo "Building Windows version using Docker..."
docker build -t quantanalysis-windows-builder -f Dockerfile.windows .
docker run --rm -v $(pwd)/dist:/app/dist quantanalysis-windows-builder

echo "Build complete!"
echo "macOS files:"
echo "  - dist/QuantAnalysis.app"
echo "  - QuantAnalysis.dmg"
echo "Windows files:"
echo "  - dist/QuantAnalysis/QuantAnalysis.exe" 