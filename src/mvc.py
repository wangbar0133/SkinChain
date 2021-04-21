import time
import json
import socket

from config import Config

from src.bin.net import Client, UdpServerSock, get_host_ip
from src.object.block import Block
from src.object.blockchain import BlockChain


class AccountOpertion(BlockChain):
    """用户操作对象"""
    def __init__(self, user):
        BlockChain.__init__(self)
        self.user_history = self.get_user_history(user)
        self.user = user

    def show_coins(self):
        """展示一个用户的所有资产"""
        coin_dict = {}
        for history in self.user_history:
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

    def show_coin_count(self):
        return len(self.show_coins())

    def show_trans_history(self):
        """查看用户的历史纪录"""
        history_list = self.get_user_history(self.user)
        user_history = []
        for history in history_list:
            if history["opt"] == "send":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "发送给" + history["recive"]
                })
            elif history["opt"] == "recive":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "收到从" + history["recive"]
                })
            elif history["opt"] == "create":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "创建"
                })
        return user_history

    def show_create(self):
        """查看用户作品"""
        coin_dict = {}
        for history in self.user_history:
            coin = history["coin"]
            if "creater" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1
        coin_list = []
        for coin in coin_dict:
            if coin_dict[coin] == 1:
                coin_list.append(coin)
        return coin_list

    def send_coin(self, recive, coin, mesg):
        """向别人交易"""
        index = BlockChain().get_top_block_index() + 1
        sender = self.user
        pr_block_hash = BlockChain().get_top_block_hash()
        Client().sync_chain(index=index - 1)
        block = Block(index, sender, recive, pr_block_hash, coin, mesg)
        if BlockChain().insert_block(block):
            Client().push_blocks([block])
        return index

    def create_coin(self, coin, mesg=None):
        """上传作品"""
        index = BlockChain().get_top_block_index() + 1
        sender = self.user
        recive = self.user
        pr_block_hash = BlockChain().get_top_block_hash()
        Client().sync_chain(index=index - 1)
        block = Block(index, sender, recive, pr_block_hash, coin, mesg)
        if BlockChain().insert_block(block):
            Client().push_blocks([block])
        return index


def server_block():
    """UDP接收端(接收区块)"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.PORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        mesg, addr = udp_server_sock.recvfrom(65535)
        mesg = json.loads(mesg.decode('utf-8'))
        request = mesg["request"]
        data = mesg["data"]
        if request == "chuanSongKuai":
            block_list = data
            for block in block_list:
                BlockChain().insert_block(block)
        elif request == "sync":
            host_index = BlockChain().get_top_block_index()
            index = data
            if host_index > index:
                block_list = []
                for sync_index in range(index, host_index + 1):
                    block_list.append(BlockChain().get_block_by_index(sync_index))
                Client().push_blocks(block_list=block_list, addr=addr)


def find_node():
    """查找网络上的节点"""
    PORT = Config.SHACKPORT
    ip_pool = Config.IPPOOL
    address = (ip_pool, PORT)
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_list = []
    for count in range(100):
        udp_cli_sock.sendto("nodefinder".encode('utf-8'), address)
        mesg, addr = udp_cli_sock.recvfrom(1024)
        if mesg == "Node".encode('utf-8'):
            ip_list.append(addr)
    ip_list = set(ip_list)
    return ip_list


def response_find_node():
    """监听并相应获取上线请求(守护进程)"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.SHACKPORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        if mesg == "nodefinder".encode('utf-8'):
            udp_server_sock.sendto(bytes("Node".encode('utf-8')), addr)


def request_sync(index=int):
    """根据索引请求同步链"""
    PORT = Config.SYNCPORT
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_pool = find_node()
    for ip in ip_pool:
        address = (ip, PORT)
        for count in range(5):
            udp_cli_sock.sendto(str(index).encode('utf-8'), address)
            time.sleep(0.2)


def response_sync():
    """(守护进程)"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.SYNCPORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        index = int(mesg.decode('utf-8'))
        if index < BlockChain().get_top_block_index():
            block_list = []


def check_block(block):
    """检查收到的块"""
    from encrypt import check_sign, check_hash
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
        db_top_index = BlockChain().get_top_block_index()
        if block_index != db_top_index + 1:
            result = False
        if block["header"]["pr_block_hash"] != BlockChain().get_top_block_hash():
            result = False
        sender = block["header"]["sender"]
        coin = block["tran"]["coin"]
        sender_obj = AccountOpertion(sender)
        coin_list = sender_obj.show_coins()
        if coin in coin_list:
            return False
    except:
        result = False
    finally:
        return result
