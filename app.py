from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ensure download directory exists if needed
os.makedirs('downloads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    download_type = data.get('type', 'video')

    if not url:
        return jsonify({'error': 'Please provide a valid media link.'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Extracted Media Stream')
            thumbnail = info.get('thumbnail', '')
            
            direct_url = ''
            if 'url' in info:
                direct_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                direct_url = info['formats'][-1].get('url', url)
            else:
                direct_url = url

        return jsonify({
            'title': title,
            'thumbnail': thumbnail,
            'download_url': direct_url,
            'type': download_type
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process container stream: {str(e)}'}), 500

# Explicit route handler for all footer links so they never show 404 Not Found
@app.route('/softonic-info')
@app.route('/security-trust')
@app.route('/support')
@app.route('/jobs')
@app.route('/editorial-guidelines')
@app.route('/add-software')
@app.route('/online-tools')
@app.route('/advertising')
@app.route('/monetization')
@app.route('/upload-manage')
@app.route('/software-policy')
@app.route('/advertising-opportunities')
@app.route('/dmca')
@app.route('/legal-information')
@app.route('/terms-of-use')
@app.route('/privacy-policy')
@app.route('/cookie-policy')
def footer_pages():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)