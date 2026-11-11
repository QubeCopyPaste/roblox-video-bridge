from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
        
    try:
        ydl_opts = {'format': 'best[ext=mp4]/best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            
        return jsonify({
            "status": "success",
            "streamUrl": stream_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)