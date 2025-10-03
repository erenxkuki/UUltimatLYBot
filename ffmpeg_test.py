from flask import Flask, render_template
import subprocess

result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
print("FFmpeg path:", result.stdout.strip())
# Keep Bot Alive

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    # debug=True để tự reload khi sửa code
    app.run(host='0.0.0.0', port=5000, debug=True)
  
