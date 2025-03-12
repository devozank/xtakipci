import os
from flask import Flask, request, render_template
import json

app = Flask(__name__)
ALLOWED_FILES = {'follower.js', 'following.js'}

def allowed_file(filename):
    return filename.lower() in ALLOWED_FILES

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if not all(k in request.files for k in ALLOWED_FILES):
            return "Gerekli dosyalar yüklenmedi"
        
        follower_file = request.files.get('follower.js')
        following_file = request.files.get('following.js')

        if not follower_file or not allowed_file(follower_file.filename):
            return "Uygun bir follower dosyası seçilmedi"
        
        if not following_file or not allowed_file(following_file.filename):
            return "Uygun bir following dosyası seçilmedi"

        followers = process_data_file(follower_file, prefix='window.YTD.follower.part0 = ')
        following = process_data_file(following_file, prefix='window.YTD.following.part0 = ')

        not_following_back = following - followers
        base_url = "https://twitter.com/intent/user?user_id="
        links = [f"{base_url}{account_id}" for account_id in not_following_back]

        return render_template('result.html', links=links)
    
    return render_template('index.html')

def process_data_file(file, prefix):
    data = file.read().decode('utf-8').strip()
    if data.startswith(prefix):
        data = data[len(prefix):].strip()
    
    json_data = json.loads(data)
    key = 'follower' if 'follower' in file.filename else 'following'
    return {entry[key]['accountId'] for entry in json_data}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))