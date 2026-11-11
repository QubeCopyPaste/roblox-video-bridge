from flask import Flask, request, jsonify
import yt_dlp
import os
import traceback

app = Flask(__name__)
app.url_map.strict_slashes = False  # Prevents trailing slash routing conflicts

@app.route('/', methods=['GET'])
def home():
    return "Roblox Video Bridge is Live!", 200

@app.route('/process', methods=['GET', 'POST'])
def process_video():
    # 1. If someone visits /process in a web browser (GET), show a status message instead of crashing
    if request.method == 'GET':
        return jsonify({
            "status": "online",
            "message": "The /process endpoint is active. Send a POST request with a JSON body containing {'url': 'YOUR_YOUTUBE_URL'}."
        }), 200

    # 2. Handle the POST request sent from Roblox Studio
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided in JSON body"}), 400

    video_url = data['url']

    try:
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
        print("CRITICAL EXCEPTION:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
