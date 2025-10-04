#!/bin/bash
set -e  # Dừng khi gặp lỗi

# --- Phần Build (chỉ cần chạy 1 lần khi deploy) ---
if [ ! -d ".venv" ]; then
    echo "[INFO] Cài đặt virtualenv và dependencies..."
    
    # Cập nhật gói và cài ffmpeg (chỉ cài 1 lần)
    apt-get update -y
    apt-get install -y ffmpeg
    
    # Tạo virtualenv
    python3 -m venv .venv
fi

# --- Kích hoạt virtualenv ---
source .venv/bin/activate

# Cập nhật pip và cài requirements
pip install --upgrade pip
pip install -r requirements.txt

# --- Chạy bot ---
echo "[INFO] Khởi chạy bot..."
python main.py
