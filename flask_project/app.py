from flask import Flask, flash, redirect,render_template, request, jsonify
import pymysql
import requests
import json
from tools import *


app = Flask(__name__)
app.secret_key = '001'
# html⽂件夹路径在此添加template_folder修改
# 默认在⽬录下的template⽂件夹中

# 打开数据库连接
db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='basedata')
 
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()
app.config['user'] = {}

"""
主页面
"""
@app.route("/")
def index():
#    print(app.config['user'])
    res = get_info_data()
    args = {"user":app.config['user'], "cloud":res["cloud"],"school":res["school"],"num":res["num"]}
    return render_template("/index.html", **args)


"""
登陆
"""
@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        # print(username)
        cursor = db.cursor()
        select_sql = "SELECT * from users where phone = '{}' ;".format(phone)
        cursor.execute(select_sql)
        info = cursor.fetchall()
        if len(info) == 0:
            flash('账号不存在，请注册')
            return redirect("/login")
        elif password == info[0][4]:
            app.config['user'] = {"name":info[0][1],"phone":info[0][2], "email":info[0][3], "identity":info[0][5]}
            # print(app.config['user'])
            return redirect("/")
        else:
            flash('账号或密码错误')
            return redirect("/login")

    return render_template('logint.html')


"""
注册
"""
@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        identity = request.form['identity']
        email = request.form['email']
        name = request.form['name']
        school = request.form['school']
        cursor = db.cursor()
        select_sql = "SELECT * from users where phone = '{}' ;".format(phone)
        cursor.execute(select_sql)
        info = cursor.fetchall()

        if len(info) == 0:
            sql = "insert into users (name,phone,email,password,identity,school) values ('%s','%s','%s','%s','%s','%s');" % (name, phone, email, password, identity, school)
            db.begin()
            cursor.execute(sql)
            db.commit()
        else:
            flash('something wrong please try again')
            return redirect("/login")
        
        return redirect("/login")

    return render_template('registert.html')




"""
用户信息展示
"""
@app.route("/userinfo")
def userinfo():
    if len(app.config['user']) == 0:
        return redirect("/login")
    args = {"user":app.config['user']}
    return render_template('user_info.html', **args)

"""
登出
"""
@app.route("/logout", methods=['POST','GET'])
def logout():
    app.config['user'] = {}
    return redirect("/")



"""
chatbot
"""
@app.route("/chatbot", methods=['POST','GET'])
def chatbot():
    if len(app.config['user']) == 0:
        return redirect("/login")
    if request.method == 'POST':
        message = request.form.get('message')
        mode = request.form.get('mode')  # 获取mode参数
        # print(f"Message: {message}, Mode: {mode}")  # 打印接收到的参数
        sql = "insert into chatlist (phone,chat) values ('%s','%s');" % ( app.config['user']['phone'],message)
        db.begin()
        cursor.execute(sql)
        db.commit()
        
        # 根据不同的mode执行不同的逻辑
        if mode == "0":  # RAG模式
            headers = {'Content-Type': 'application/json'}
            data = {"prompt": message}
            response = requests.post(url='http://127.0.0.1:1024', headers=headers, data=json.dumps(data)).json()["response"]
        else:  # Agent模式
            headers = {'Content-Type': 'application/json'}
            data = {"prompt": message}
            response = requests.post(url='http://127.0.0.1:2048', headers=headers, data=json.dumps(data)).json()["response"]

            
        return jsonify({'message': message, 'response': response})
    args = {"user":app.config['user']}
    return render_template('chatbot.html', **args)


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=6006)