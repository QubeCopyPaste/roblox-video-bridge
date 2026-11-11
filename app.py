from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)
app.url_map.strict_slashes = False

# Public Piped API instances that handle the YouTube bypassing for you
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.drgns.space",
    "https://api.piped.private.coffee"
]

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/', methods=['GET'])
def home():
    return "Roblox Piped Bridge is Live!", 200

@app.route('/process', methods=['GET', 'POST'])
def process_video():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "Send a POST request with {'url': 'YOUTUBE_URL'}"}), 200

    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    video_url = data['url']
    video_id = extract_video_id(video_url)
    
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL format"}), 400

    stream_url = None
    title = "Unknown"

    # Rotate through public Piped instances to find one that responds instantly
    for instance in PIPED_INSTANCES:
        try:
            api_url = f"{instance}/streams/{video_id}"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                vid_data = response.json()
                title = vid_data.get('title', 'Unknown')
                
                # Piped returns an array of video streams; grab the best playable audio/video or video-only stream URL
                streams = vid_data.get('videoStreams', [])
                if streams:
                    # Look for a stream that has a direct URL
                    for s in streams:
                        if 'url' in s:
                            stream_url = s['url']
                            break
                
                if stream_url:
                    break
        except Exception:
            continue

    if not stream_url:
        return jsonify({"error": "Failed to fetch stream from alternative backend"}), 500

    return jsonify({
        "status": "success",
        "title": title,
        "streamUrl": stream_url
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
