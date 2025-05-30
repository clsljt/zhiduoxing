from flask import Flask, flash, redirect,render_template, request, url_for
import pymysql


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
# cursor = db.cursor()

global user = {"name":"clsljt","phone":"0"}


@app.route("/")
def index():
   
   return render_template("/index.html", user = user)



@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        # print(username)

        print(password)
        flash('密码不一致，请重新输入。')
        return redirect("/login")
    return render_template('logint.html')



@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
            

            return redirect("/login")

    return render_template('register.html')

@app.route("/userinfo")
def userinfo():
    if len(user) == 0:
        return redirect("/login")
    args = user
    return render_template('user_info.html', **args)


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=6006)