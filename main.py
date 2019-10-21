# _*_ coding:UTF-8 _*_
from flask_uploads import UploadSet, IMAGES, configure_uploads, ALL, TEXT
from flask import request, Flask, redirect, url_for, render_template, jsonify
import os
import re
import sqlite3
from flask import g
import time



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
        data = {'flag':'00','msg':'上传成功','filename':filename}
        return jsonify(data)
    return render_template('upload.html')

@app.route('/photo/<name>')
def show(name):
    if name is None:
        os.abort(404)
    url = photos.url(name)
    return render_template('show.html', url=url, name=name)

@app.route('/parsing')
def parsing():
    filename=request.args.get("filename")
    print("------------")
    print(filename)
    if filename is None:
        os.abort(404)
    filepath=photos.path(filename)
    dir=readFile(filepath)

    data = {'flag': '00', 'msg': '解析成功', 'filename': filename}
    return jsonify(data)

@app.route('/query')
def query():
    return jsonify(query_db("select * from binlog"))

####DB
DATABASE = 'DB/binlog.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def update_db(query):
    db=get_db()
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 执行sql语句
    cursor.execute(query)
    # 提交到数据库执行
    db.commit()
    cursor.close()
def updateSql(method,dir):
    #{'start':start,'end':end,'time':time,'sql':sql}
    start = dir['start']
    end = dir['end']
    timedate = dir['time']
    sql = dir['sql']

    filepath = dir['filepath']
    print(sql+"********************************************")
    nowTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    update_db("INSERT INTO binlog VALUES (NULL,'"+filepath.replace("/", "//")+"','"+method+"',"+start+","+end+",'"+timedate+"','"+sql.replace("'", "''")+"','"+nowTime+"');" )

####方法
#解析文件
def readFile(filepath):
    deleteArray = []
    insertArray =[]
    updateArray =[]
    with open(filepath, "r", encoding='UTF-8') as f:
        str = ""
        for line in f:
            if line.__contains__("# at"):
                arrayAppend(deleteArray,insertArray,updateArray,str)
                str = ""
            str += line
        arrayAppend(deleteArray, insertArray, updateArray, str)
    # DELETE
    for i in range(len(deleteArray)):
        a=arrayComm(deleteArray[i]);
        a['filepath']=filepath
        updateSql("DELETE",a)


     # INSTER
    for i in range(len(insertArray)):
        a = arrayComm(insertArray[i]);
        a['filepath'] = filepath
        updateSql("INSERT", a)
    #UPDATE
    for i in range(len(updateArray)):
        a=arrayComm(updateArray[i]);
        a['filepath']=filepath
        updateSql("UPDATE",a)




#判断类型添加到数组
def arrayAppend(arr,arr2,arr3,str):
    if str.find("DELETE") != -1:
        arr.append(str)
    elif str.find("INSERT") != -1:
        arr2.append(str)
    elif str.find("UPDATE") != -1:
        arr3.append(str)
#数组公共解析
def arrayComm(str):
    s=re.search('# at (\d+)',str)
    # 开始节点
    start =s.group(1)
    s=re.search('end_log_pos (\d+)',str)
    # 结束节点
    end =s.group(1)
    s = re.search('(\w+)\s\w{2}:\w{2}:\w{2}', str)
    #时间
    time = s.group()
    date=s.group(1)
    prefix="20"+date[0:2]+"-"+date[2:4]+"-"+date[4:6]
    print(prefix)
    time=time.replace(date,prefix)
    s = re.search('###[\s\S]+', str)
    #sql
    sql = s.group().replace("###", "")
    return {'start':start,'end':end,'time':time,'sql':sql}

if __name__ == '__main__':
    app.run()
