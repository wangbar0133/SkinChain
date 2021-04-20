from flask import Flask, render_template, request, redirect, session

from src.encrypt import check_password, file_hash
from src.account import Account, AccountOpertion, BlockChain
from src.bin import copy_file

from config import Config


app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH


@app.route('/', methods=['POST', 'GET'])
def root():
    return render_template('root.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    status = "请输入账户密码"
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


@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect('/login/')


@app.route('/create/', methods=['POST', 'GET'])
def create():
    username, password = Account().create_account()
    return render_template('create.html',
                           username=username,
                           password=password)


@app.route('/user/<user>/', methods=['POST', 'GET'])
def user(user):
    if user == session.get("username") and session.get("password"):
        user_obj = AccountOpertion(user)
        username = user
        coin_count = user_obj.show_coin_count()
        return render_template('user.html',
                               username=username,
                               coin_count=coin_count)
    else:
        return redirect('/login/')


@app.route('/user/', methods=['POST', 'GET'])
def re_login():
    if session.get("password") and session.get("username"):
        username = session.get("username")
        return redirect('/user/' + username + '/')
    else:
        return redirect('/login/')


@app.route('/user/<user>/tran/', methods=['POST', 'GET'])
def tran(user):
    if session.get("password") and session.get("username"):
        username = session.get("password")
        return redirect('/user/' + username + '/')
    else:
        user_obj = AccountOpertion(user)
        coin_list = user_obj.show_coins()
        if request.method == 'POST':
            obj_username = request.form.get("obj_username")
            coin = request.form.get("coin")
            message = request.form.get("message")
            index = user_obj.send_coin(recive=obj_username, coin=coin, mesg=message)
            return redirect('/user/' + user + "/tran/succese/" + index + "/")
        return render_template("tran.html",
                               coin_list=coin_list)


@app.route('/user/<user>/tran/succese/<index>', methods=['POST', 'GET'])
def succese(user, index):
    import time
    block = BlockChain().get_block_by_index(index)
    recive = block["tran"]["recive"]
    time = time.asctime(time.localtime(block["header"]["timestamp"]))
    coin = block["tran"]["coin"]
    return render_template("succese.html",
                           sender=user,
                           recive=recive,
                           time=time,
                           coin=coin)


@app.route('/user/<user>/showtrans/', methods=['POST', 'GET'])
def show_trans(user):
    user_obj = AccountOpertion(user)
    trans = user_obj.show_trans_history()
    return render_template("showtrans.html",
                           trans=trans)


@app.route('user/<user>/showcoins', methods=['POST', 'GET'])
def show_coins(user):
    user_obj = AccountOpertion(user)
    coin_list = user_obj.show_coins()
    return render_template("showcoins.html",
                           coin_list=coin_list,
                           username=user)


@app.route('/user/<user>/upload/', methods=['POST', 'GET'])
def upload(user):
    return render_template("upload.html", user=)


@app.route('/uploader/', methods=['POST', 'GET'])
def uploader():
    file_path = request.get("filepath")
    file_hash_value = file_hash(file_path)
    dst_path = Config.UPLOAD_FOLDER + file_hash_value
    if copy_file(file_path, dst_path):

    else:
        data = {
            "status": "err"
        }
    return data




if __name__ == '__main__':
    app.run(debug=True)
