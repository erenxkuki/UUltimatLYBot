# build.sh
#!/bin/bash
set -e

apt-get update -y
apt-get install -y ffmpeg

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
