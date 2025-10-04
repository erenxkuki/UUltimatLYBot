#!/bin/bash

# Cập nhật gói
apt-get update -y

# Cài ffmpeg
apt-get install -y ffmpeg

# Thiết lập virtualenv (nếu muốn)
python3 -m venv .venv
source .venv/bin/activate

# Cài requirements
pip install --upgrade pip
pip install -r requirements.txt

# Chạy bot
python main.py
