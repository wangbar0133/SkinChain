from flask import Flask, render_template, request, redirect, session

from src.bin.encrypt import check_password, file_hash
from src.object.account import Account
from src.mvc import AccountOpertion, BlockChain
from src.bin.os import move_file, return_img_stream, get_pic_path
from src.bin.net import send_file
from src.bin.log import Log

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
    if session.get("username") and session.get("password"):
        return redirect('/user/' + session.get("username") + '/')
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


@app.route('/tran/', methods=['POST', 'GET'])
def go_tran():
    if session.get("password") and session.get("username"):
        username = session.get("username")
        return redirect('/user/' + username + '/tran/')
    else:
        return redirect('/login/')


@app.route('/user/<user>/tran/', methods=['POST', 'GET'])
def tran(user):
    user_obj = AccountOpertion(user)
    coin_list = user_obj.show_coins()
    pic_path_list = []
    for coin in coin_list:
        pic_path_list.append({
            "coin": coin,
            "path": get_pic_path(coin)
        })
    if request.method == 'POST':
        obj_username = request.form.get("obj_username")
        coin = request.form.get("coin")
        message = request.form.get("message")
        index = user_obj.send_coin(recive=obj_username, coin=coin, mesg=message)
        return redirect('/user/' + user + "/tran/succese/" + index + "/")
    return render_template("tran.html",
                           pic_path_list=pic_path_list)


@app.route('/user/<user>/tran/succese/<index>', methods=['POST', 'GET'])
def succesed_tran(user, index):
    block = BlockChain().get_block_by_index(index)
    recive = block["tran"]["recive"]
    time = block["header"]["timestamp"]
    coin = block["tran"]["coin"]
    path = get_pic_path(coin)
    return render_template("succesetran.html",
                           sender=user,
                           recive=recive,
                           time=time,
                           coin=coin,
                           path=path)


@app.route('/user/<user>/showtrans/', methods=['POST', 'GET'])
def show_trans(user):
    user_obj = AccountOpertion(user)
    trans = user_obj.show_trans_history()
    return render_template("showtrans.html",
                           trans=trans)


@app.route('/user/<user>/showcoins/', methods=['POST', 'GET'])
def show_coins(user):
    user_obj = AccountOpertion(user)
    coin_list = user_obj.show_coins()
    pic_path_list = []
    for coin in coin_list:
        pic_path_list.append({
            "coin": coin,
            "path": get_pic_path(coin)
        })
    return render_template("showcoins.html",
                           pic_path_list=pic_path_list,
                           username=user)


@app.route('/upload/', methods=['POST', 'GET'])
def upload():
    if not (session.get("username") and session.get("password")):
        return redirect('/login/')
    username = session.get("username")
    return render_template("upload.html", username=username)


@app.route('/uploader/', methods=['POST', 'GET'])
def uploader():
    username = session.get("username")
    print(request.files.get("photo"))
    # img = request.files["photo"]
    # mesg = request.form.get("mesg")
    # file_path = Config.UPLOAD_FOLDER + "temp" + img.filename
    # img.save(file_path)
    """
    file_hash_value = file_hash(file_path)
    dst_path = Config.UPLOAD_FOLDER + file_hash_value
    if move_file(file_path, dst_path):
        send_file(dst_path)
        user_obj = AccountOpertion(username)
        index = user_obj.create_coin(coin=file_hash_value, mesg=mesg)
        return redirect("/uploader/" + str(index) + "/")
    """

@app.route('/uploader/fail/', methods=['POST', 'GET'])
def upload_fail():
    return render_template("uploadfail.html")


@app.route('/uploader/<index>/', methods=['POST', 'GET'])
def upload_ok(index):
    import time
    block = BlockChain().get_block_by_index(index)
    time = time.asctime(time.localtime(block["header"]["timestamp"]))
    coin = block["tran"]["coin"]
    path = get_pic_path(coin)
    return render_template("succeseupload.html",
                           time=time,
                           coin=coin,
                           path=path)


@app.route('/coin/<coin>/', methods=['POST', 'GET'])
def coin(coin):
    coin_history = BlockChain().get_coin_history(coin)
    path = get_pic_path(coin)
    return render_template("coin.html",
                           coin_history=coin_history,
                           path=path)


if __name__ == '__main__':
    app.run(debug=True)
