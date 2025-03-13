# pip install flask


# 필요한 모듈 import, 기본 설정
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import time
import os

# 웹 서버 만들기
app = Flask(__name__, static_folder='public', static_url_path='/public', template_folder='template')

########
# 초기화 작업들
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "public", "data")
if not os.path.exists(DATA_FILE_PATH):
    os.makedirs(DATA_FILE_PATH)


@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/hi')
def hi():
    return "Hi, World!"


# http://localhost:7070/echo?msg=hello
@app.route('/echo')
def echo():
    msg = request.args.get('msg', None)
    if msg is None:
        return "no message"
    return msg


# curl -X POST -H "Content-Type: application/json" -d "{\"count\": 2}" http://127.0.0.1:7070/random
@app.route('/random', methods=['POST'])
def randomNumer():
    count = None
    try:
        count = request.json['count']
    except:
        pass
    if count is None:
        return jsonify([])

    random_numbers = {f'num{i}': random.randint(0, 1000) for i in range(count)}
    return jsonify(random_numbers)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        file = request.files['file']
        if file:
            filename = os.path.join(DATA_FILE_PATH, file.filename)
            file.save(filename)
            return redirect(url_for("showfiles"))
        return "File not found"


# curl http://localhost:7070/showfiles
@app.route("/showfiles")
def showfiles():
    files = []
    for file in os.listdir(DATA_FILE_PATH):
        # 디렉터리를 제외하고 파일명만 추출
        filename = os.path.basename(file)
        files.append({
            "filename": filename,
            "url": f"/public/data/{filename}"
        })
    return render_template("files.html", files=files)


@app.route("/deleteall")
def deleteall():
    for file in os.listdir(DATA_FILE_PATH):
        os.remove(os.path.join(DATA_FILE_PATH, file))
    return "All files deleted"


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=7070,
        debug=True
    )
