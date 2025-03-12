import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import zipfile
import json
from io import BytesIO

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'zip'}
REQUIRED_FILES = {'data/follower.js', 'data/following.js'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Dosya yüklenmedi"
        
        file = request.files['file']
        if file.filename == '':
            return "Dosya seçilmedi"
        
        if file and allowed_file(file.filename):
            file_bytes = file.read()
            links = process_zip_file(file_bytes)
            return render_template('result.html', links=links)
    
    return render_template('index.html')

def process_zip_file(file_bytes):
    links = []
    with zipfile.ZipFile(BytesIO(file_bytes), 'r') as zip_ref:
        for file_name in REQUIRED_FILES:
            if file_name in zip_ref.namelist():
                with zip_ref.open(file_name) as f:
                    data = f.read().decode('utf-8')
                    prefix = 'window.YTD.follower.part0 = ' if 'follower' in file_name else 'window.YTD.following.part0 = '
                    json_data = load_json_data(data, prefix)
                    if 'follower' in file_name:
                        followers = {entry['follower']['accountId'] for entry in json_data}
                    else:
                        following = {entry['following']['accountId'] for entry in json_data}

        not_following_back = following - followers
        base_url = "https://twitter.com/intent/user?user_id="
        links = [f"{base_url}{account_id}" for account_id in not_following_back]

    return links

def load_json_data(data, prefix_to_remove):
    data = data.strip()
    if data.startswith(prefix_to_remove):
        data = data[len(prefix_to_remove):].strip()
    return json.loads(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))