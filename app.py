from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# Ensure download directory exists
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
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
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Extracted Media Stream')
            thumbnail = info.get('thumbnail', '')
            
            # Get filename for local download route
            filename = ydl.prepare_filename(info)
            if download_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            relative_filename = os.path.basename(filename)

        return jsonify({
            'title': title,
            'thumbnail': thumbnail,
            'download_url': f'/get-file/{relative_filename}',
            'type': download_type
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process container stream: {str(e)}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"File not found or expired: {str(e)}", 404

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
