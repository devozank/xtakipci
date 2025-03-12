import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import zipfile
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
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
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # ZIP dosyasını aç ve içindeki JSON dosyalarını işle
            links = process_zip_file(filepath)
            return render_template('result.html', links=links)
    
    return render_template('index.html')

def process_zip_file(filepath):
    links = []
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Yalnızca gereken dosyaları çıkart
        for file_name in file_list:
            if file_name in REQUIRED_FILES:
                zip_ref.extract(file_name, app.config['UPLOAD_FOLDER'])

    follower_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'follower.js')
    following_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'following.js')

    if os.path.exists(follower_path) and os.path.exists(following_path):
        follower_data = load_json_data(follower_path, 'window.YTD.follower.part0 = ')
        following_data = load_json_data(following_path, 'window.YTD.following.part0 = ')

        followers = {entry['follower']['accountId'] for entry in follower_data}
        following = {entry['following']['accountId'] for entry in following_data}

        not_following_back = following - followers
        base_url = "https://twitter.com/intent/user?user_id="
        
        links = [f"{base_url}{account_id}" for account_id in not_following_back]

    # İşlemi tamamlanan dosyaları temizle
    clean_up_files([follower_path, following_path, filepath])

    return links

def load_json_data(file_path, prefix_to_remove):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().strip()
        if data.startswith(prefix_to_remove):
            data = data[len(prefix_to_remove):].strip()
        return json.loads(data)

def clean_up_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))