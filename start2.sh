#!/bin/bash
set -e

# --- CẬP NHẬT HỆ THỐNG & CÀI THÊM FFMPEG ---
apt-get update -y
apt-get install -y ffmpeg

# --- TẠO VIRTUALENV ---
python3 -m venv .venv
source .venv/bin/activate

# --- CÀI THÊM REQUIREMENTS ---
pip install --upgrade pip
pip install -r requirements.txt

# --- CHẠY BOT ---
python main.py
