# -*-coding:utf-8-*-
import json
import time
import socket
import threading
import pymongo
import os

from bson import json_util

from config import Config
from src.bin.log import Log
from src.bin.encrypt import check_sign, check_hash


def get_host_ip():
    """返回本机IP地址"""
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(('8.8.8.8', 8070))
    ip = ss.getsockname()[0]
    ss.close()
    return ip


def send_file(path):
    """向全网广播文件，输入文件路径"""
    addr = (Config.IPPOOL, Config.FILEPORT)
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        f = open(path, 'rb')
    except Exception as e:
        Log().error("路径文件不存咋：" + str(e))
    count = 0
    while True:
        if count == 0:
            data = bytes(path,  encoding="utf8")
            udp_cli_sock.sendto(data, addr)
        data = f.read(1024)
        if str(data) != "b''":
            udp_cli_sock.sendto(data, addr)
        else:
            udp_cli_sock.sendto('end'.encode('utf-8'), addr)
            break
        count += 1
    udp_cli_sock.close()


def recive_file():
    """接收文件(守护进程)"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.FILEPORT))
    count = 0
    while True:
        if count == 0:
            data, client_addr = udp_server_sock.recvfrom(1024)
            f = open(data, 'wb')
        data, client_addr = udp_server_sock.recvfrom(1024)
        if str(data) != "b'end'":
            f.write(data)
        else:
            f.close()
            break
        udp_server_sock.sendto('ok'.encode('utf-8'), client_addr)
        count += 1


class Client(object):
    """UDP发送端(发送区块相关)"""
    def __init__(self):
        udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_cli_sock = udp_cli_sock
        self.addr = (Config.IPPOOL, Config.PORT)

    def _push(self, request, data, addr=None):
        mesg = {
            "request": request,
            "data": data
        }
        if addr:
            self.udp_cli_sock.sendto(json_util.dumps(mesg).encode('utf-8'), addr)
        else:
            self.udp_cli_sock.sendto(json_util.dumps(mesg).encode('utf-8'), self.addr)
        self.udp_cli_sock.close()

    def push_blocks(self, block_list, addr=None):
        self._push(request="chuanSongKuai", data=block_list, addr=addr)

    def sync_chain(self, index):
        self._push(request="sync", data=index)


class UdpServerSock(object):
    """获取区块接收Sock"""
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((get_host_ip(), Config.PORT))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock = sock


class Node(object):
    """获取存活节点"""
    def __init__(self):
        IPPOOL = Config.IPPOOL
        conf = IPPOOL.split(".")
        ip_prefix = ""
        for count in range(0, 3):
            if conf[count] != "255":
                ip_prefix = ip_prefix + conf[count] + "."

        self.ip_pool = list()
        for count in range(1, 255):
            self.ip_pool.append(ip_prefix + str(count))

        self.ip_alive_list = list()
        self.ip_list = list()

    def __ping(self, ip):
        cmd = "ping -n 1 " + ip + '|findstr TTL'
        res = os.popen(cmd)
        if res.readlines():
            self.ip_alive_list.append(ip)

    def __ping_mongod(self, ip):
        try:
            myclient = pymongo.MongoClient(host=ip, port=27017, serverSelectionTimeoutMS=50, socketTimeoutMS=50)
            dblist = myclient.list_database_names()
            if dblist:
                self.ip_list.append(ip)
        except:
            pass

    def find(self):
        thread_list = list()

        for ip in self.ip_pool:
            thread_list.append(threading.Thread(target=self.__ping, args=(ip,)))

        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()

        thread_mongod_list = list()

        for ip in self.ip_alive_list:
            thread_mongod_list.append(threading.Thread(target=self.__ping_mongod, args=(ip,)))

        self.ip_list = list()

        for thread in thread_mongod_list:
            thread.start()

        for thread in thread_mongod_list:
            thread.join()

        return self.ip_list


class Mongodb(object):

    def __init__(self, ip):
        try:
            myclient = pymongo.MongoClient(host=ip, port=27017)
            dblist = myclient.list_database_names()
            if "skin_chain" not in dblist:
                mydb = myclient["skin_chain"]
            else:
                mydb = myclient["skin_chain"]
            self.mycol = mydb["chain"]
        except:
            pass
        self.ip = ip

    def test(self, user):
        block_list = json_util.dumps(self.mycol.find({"header.sender": user}, {"_id": False}))
        return block_list

    def insert(self, block):
        """在数据库插入新的块"""
        try:
            self.mycol.insert_one(block.block_dict)
            return True
        except Exception as e:
            Log().error("区块插入失败：" + str(e))
            print(e)
            return False

    def insert_dict(self, block):
        self.mycol.insert_one(block)

    def delete(self, index):
        """根据索引删除块"""
        try:
            self.mycol.delete_one({"header.index": index})
        except Exception as e:
            Log().error("删除失败：" + str(e))

    def clean(self):
        """清空数据库"""
        try:
            self.mycol.delete_many({})
        except Exception as e:
            Log().error("清空数据库失败：" + str(e))

    def get_chain(self):
        block = self.mycol.find({}, {"_id": False}).sort("_id", 1)
        return json.loads(json_util.dumps(block))

    def get_top_block(self):
        """获取最新的块"""
        block = self.mycol.find({}, {"_id": False}).sort("_id", -1).limit(1)
        return json.loads(json_util.dumps(block))[0]

    def get_chain_len(self):
        """获取链的长度"""
        return self.mycol.count()

    def get_block_by_index(self, index):
        """通过索引获取最新的块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({"header.index": index}, {"_id": False})))[0]
        except Exception as e:
            Log().error("获取最新块失败：" + str(e))

    def get_block_list_by_user(self, user):
        """获取含有某一用户的所有块"""
        try:
            block_list_raw = json.loads(json_util.dumps(self.mycol.find({"header.sender": user}, {"_id": False}))) \
                             + json.loads(json_util.dumps(self.mycol.find({"tran.recive": user}, {"_id": False})))
            block_list = []
            for item in block_list_raw:
                if item not in block_list:
                    block_list.append(item)
            return block_list
        except Exception as e:
            Log().error("通过用户获取块失败：" + str(e))

    def get_block_list_by_coin(self, coin):
        """获取含有某一资产的所有块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({"tran.coin": coin}, {"_id": False})))
        except Exception as e:
            Log().error("通过资产获取块失败：" + str(e))

    def get_max_index(self):
        return int(self.get_chain_len()) - 1

    def get_top_block_hash(self):
        top_block = self.get_top_block()
        return top_block["block_hash"]

    def get_user_history(self, user):
        block_list = self.get_block_list_by_user(user)
        if not block_list:
            return False
        user_history_list = []
        for block in block_list:
            if block["header"]["sender"] == user and block["tran"]["recive"] != user:
                user_history_list.append({
                    "opt": "send",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "recive": block["tran"]["recive"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["tran"]["recive"] == user and block["header"]["sender"] != user:
                user_history_list.append({
                    "opt": "recive",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "sender": block["header"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["tran"]["recive"] == user and block["header"]["sender"] == user:
                user_history_list.append({
                    "opt": "create",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "creater": block["header"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
        user_history_list = sorted(user_history_list, key=lambda i: i['timestamp'])
        for index, coin in enumerate(user_history_list):
            user_history_list[index]["timestamp"] = time.asctime(time.localtime(int(float(coin["timestamp"]))))
        return user_history_list

    def show_coins(self, user):
        """展示一个用户的所有资产"""
        coin_dict = {}
        user_history = self.get_user_history(user)
        if not user_history:
            return []
        for history in user_history:
            coin = history["coin"]
            if "recive" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1
            elif "sender" in history.keys():
                try:
                    coin_dict[coin] = coin_dict[coin] - 1
                except:
                    print("err")
            elif "creater" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1

        coin_list = []
        for coin in coin_dict:
            if coin_dict[coin] == 1:
                coin_list.append(coin)
        return coin_list


def check_net_block(block, ip):
    """检查块"""
    result = True
    try:
        string = block["header"].__str__() + block["trans_list"].__str__()
        sig = block["sign"]
        user_name = block["header"]["sender"]
        hash_value = block["block_hash"]
        if not check_sign(string, sig, user_name):
            result = False
        if not check_hash(string, hash_value):
            result = False
        block_index = int(block["header"]["index"])
        db = Mongodb(ip)
        db_top_index = db.get_max_index()
        if block_index != db_top_index + 1:
            result = False
        if block["header"]["pr_block_hash"] != db.get_top_block_hash():
            result = False
        sender = block["header"]["sender"]
        coin = block["tran"]["coin"]
        coin_list = db.show_coins(sender)
        if coin in coin_list:
            return False
    except Exception as e:
        Log().error("检查区块合法性失败：" + str(e))
        result = False
    finally:
        return result


class Sync_mongod(object):
    """同步数据库"""
    def __init__(self):
        self.ip_list = Node().find()
        self.local_db = Mongodb("localhost")
        self.db_dict = {}
        for ip in self.ip_list:
            self.db_dict[ip] = Mongodb(ip)

    def get_max_index(self):
        index_dict = {}
        for db in self.db_dict.values():
            index_dict[db.ip] = db.get_max_index()
        print(index_dict)
        max_ip = max(index_dict, key=index_dict.get)
        max_index = index_dict[max_ip]
        return max_ip, max_index

    def get_block_list(self, index1, index2, ip):
        db = self.db_dict[ip]
        block_list = list()
        for index in range(index1 + 1, index2 + 1):
            block_list.append(db.get_block_by_index(index))
        return block_list

    def add_block_list_to_net(self, ip, block_list):
        db = self.db_dict[ip]
        for block in block_list:
            if check_net_block(block, ip):
                db.insert(block)

    def sync(self):
        local_index = self.local_db.get_max_index()
        max_ip, max_index = self.get_max_index()
        if local_index > max_index:
            for ip in self.db_dict.keys():
                block_list = self.get_block_list(max_index, local_index, "local_host")
                self.add_block_list_to_net(ip, block_list)
        elif local_index > max_index:
            block_list = self.get_block_list(local_index, max_index, max_ip)
            self.add_block_list_to_net("localhost", block_list)


if __name__ == "__main__":
    print(Node().find())
    # print(Sync_mongod().ip_list)
