from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Video Bridge is Live!", 200

@app.route('/process', methods=['POST'])
def process_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    video_url = data['url']

    try:
        # Add extractor arguments and user agent flags to dodge cloud blocking
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'Unknown')

        return jsonify({
            "status": "success",
            "title": title,
            "streamUrl": stream_url
        })

    except Exception as e:
        print("CRITICAL ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
