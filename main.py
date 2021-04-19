from flask import Flask, render_template, request, redirect, session

from src.bin.encrypt import check_password
from src.user.account import Account

from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY


@app.route('/', methods=['POST', 'GET'])
def root():
    session.clear()
    return render_template('root.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    status = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if check_password(username, password):
            session["username"] = username
            session["password"] = password
            return redirect('/user/' + username + '/')
        else:
            status = "账户/密码错误"
    return render_template('login.html',
                           status=status)


@app.route('/create/', methods=['POST', 'GET'])
def create():
    username, password = Account().create_account()
    return render_template('create.html',
                           username=username,
                           password=password)


@app.route('/user/<user>/', methods=['POST', 'GET'])
def user(user):
    return render_template('user.html')


@app.route('/user/', methods=['POST', 'GET'])
def re_login():
    if session.get("password") and session.get("username"):
        username = session.get("password")
        return redirect('/user/' + username + '/')
    else:
        return redirect('/login/')


if __name__ == '__main__':
    app.run(debug=True)
