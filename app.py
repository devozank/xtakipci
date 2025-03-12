import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import zipfile
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Yüklenen dosyaya izin verilen uzantılar
ALLOWED_EXTENSIONS = {'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Dosya kontrolü
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
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(app.config['UPLOAD_FOLDER'])

    follower_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'follower.js')
    following_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'following.js')

    follower_data = load_json_data(follower_path, 'window.YTD.follower.part0 = ')
    following_data = load_json_data(following_path, 'window.YTD.following.part0 = ')
    
    followers = {entry['follower']['accountId'] for entry in follower_data}
    following = {entry['following']['accountId'] for entry in following_data}
    
    not_following_back = following - followers
    base_url = "https://twitter.com/intent/user?user_id="

    return [f"{base_url}{account_id}" for account_id in not_following_back]

def load_json_data(file_path, prefix_to_remove):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().strip()
        if data.startswith(prefix_to_remove):
            data = data[len(prefix_to_remove):].strip()
        return json.loads(data)

if __name__ == '__main__':
    # Uploads klasörü yoksa oluştur
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))