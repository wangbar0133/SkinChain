# -*-coding:utf-8-*-
import json
import socket
import threading
import pymongo
import os

from bson import json_util

from config import Config
from src.bin.log import Log


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

    def _ping(self, ip):
        cmd = "ping -n 1 " + ip + '|findstr TTL'
        res = os.popen(cmd)
        if res.readlines():
            self.ip_alive_list.append(ip)

    def _ping_mongod(self, ip):
        try:
            myclient = pymongo.MongoClient(host=ip, port=27017, serverSelectionTimeoutMS=50, socketTimeoutMS=50)
            dblist = myclient.list_database_names()
            if "skin_chain" in dblist:
                self.ip_list.append(ip)
        except:
            pass

    def find(self):
        thread_list = list()

        for ip in self.ip_pool:
            thread_list.append(threading.Thread(target=self._ping, args=(ip,)))

        for thread in thread_list:
            thread.start()

        thread_mongod_list = list()

        for ip in self.ip_alive_list:
            thread_mongod_list.append(threading.Thread(target=self._ping_mongod, args=(ip,)))

        self.ip_list = list()

        for thread in thread_mongod_list:
            thread.start()

        for thread in thread_mongod_list:
            thread.join()

        return self.ip_list


if __name__ == "__main__":
    print(Node().find())
