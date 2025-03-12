import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json
    file_type = data['fileType']
    account_ids = data['accountIds']

    # Gelen hesap ID'lerini işleme
    if file_type == 'follower':
        print('Follower hesap IDleri:', account_ids)
    elif file_type == 'following':
        print('Following hesap IDleri:', account_ids)

    # Bu hesap kimliklerini bir veri yapılandırma veya karşılaştırma için kullanabiliriz.
    # Örnek olarak sadece başarı mesajı dönülüyor.
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))