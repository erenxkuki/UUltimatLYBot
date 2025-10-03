from flask import Flask, render_template
import subprocess
import os

# Kiểm tra vị trí ffmpeg
result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
print("FFmpeg path:", result.stdout.strip())

# Khai báo Flask và set template_folder = thư mục hiện tại
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def home():
    return render_template("index.html")  # giờ có thể load trực tiếp file cùng folder

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
