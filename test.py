import socket
import time
import json
import ed25519
import os
from config import Config
import pymongo


if __name__ == "__main__":
    mesg = {'request': 'chuanSongKuai', 'data': [{'header': {'index': 2, 'pr_block_hash': 'b91c10afbf0627a79ef7ce9b40f5615f7f635eb3753cc66ecd122c41a402fbf8', 'timestamp': '1619197311.6868944', 'sender': '2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6'}, 'tran': {'recive': '2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6', 'coin': 'e81d7da740ae8042e24666450dbc9d24', 'mesg': '2'}, 'sign': 'U6yYk2WHuGf5BuL9OtHvdtwdg5hV3ykCERzWQczNg94vhW5nN+P/QVeMSAlRe0GvplEif9vjhYM83qexgJvaDw', 'block_hash': '89a66604a26b5a5c667c1223d58a5bdac50956f112baf0f6181705897c2f4627'}]}

    print(json.dumps(mesg).encode('utf-8'))


