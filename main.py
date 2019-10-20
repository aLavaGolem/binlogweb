from flask_uploads import UploadSet, IMAGES, configure_uploads, ALL, TEXT
from flask import request, Flask, redirect, url_for, render_template, jsonify
import os
import json

app = Flask(__name__)
app.config['UPLOADED_PHOTO_DEST'] = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADED_PHOTO_ALLOW'] = TEXT
# def dest(name):
#     return '{}/{}'.format(UPLOAD_DEFAULT_DEST, name)
#app.config['UPLOAD_PHOTO_URL'] = 'http://localhost:5000/'
photos = UploadSet('PHOTO')


configure_uploads(app, photos)

@app.route('/')
def index():
    return redirect('upload')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        print(request.files['photo'])
        filename = photos.save(request.files['photo'],folder='upload')
        data = {'flag':'00','msg':'成功','filename':filename}
        return jsonify(data)
    return render_template('upload.html')

@app.route('/photo/<name>')
def show(name):
    if name is None:
        os.abort(404)
    url = photos.url(name)
    return render_template('show.html', url=url, name=name)

app.run()