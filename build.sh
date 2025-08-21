#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create static/data directory if it doesn't exist
mkdir -p static/data

# Copy JSON files to ensure they're available
echo "📁 JSON dosyaları kontrol ediliyor..."
ls -la static/data/

# Set permissions
chmod -R 755 static/
chmod -R 644 static/data/*.json

echo "✅ Build tamamlandı!"
