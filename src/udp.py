import socket
import time
import json

from config import Config
from account import check_block, BlockChain


def get_host_ip():
    """返回本机IP地址"""
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(('8.8.8.8', 8070))
    ip = ss.getsockname()[0]
    ss.close()
    return ip


def udp_listen():
    """监听UDP请求"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.PORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        if bytes("request:".encode('utf-8')) in mesg:
            mesg = json.loads(str(mesg, encoding="utf-8"))
            request = mesg["request"]
            data = mesg["data"]
            if request == "nodefinder":
                udp_server_sock.sendto(bytes("Node".encode('utf-8')), addr)
            elif request == "QingQiuTongBuKuai":
                data = str(mesg, encoding="utf-8")
                data = json.loads(data)
                index = data["index"]
                block = BlockChain().get_block_by_index(index)
                request = "FaSongKuai"
                response = "YiShouDaoKuai"
                data = block
            else:
                block = str(mesg, encoding="utf-8")
                if check_block(block):
                    for i in range(10):
                        if BlockChain().insert_block(block):
                            udp_server_sock.sendto(bytes("yishoudaoqukuai".encode('utf-8')), addr)
                            break


def find_node():
    """查找网络上的节点"""
    PORT = Config.SHACKPORT
    ip_pool = Config.IPPOOL
    address = (ip_pool, PORT)
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_list = []
    for count in range(100):
        udp_cli_sock.sendto("nodefinder".encode('utf-8'), address)
        mesg, addr = udp_cli_sock.recvfrom(1024)
        if mesg == "nodeinfo".encode('utf-8'):
            ip_list.append(addr)
    ip_list = set(ip_list)
    return ip_list


def node_info():
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.PORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        if mesg.decode("utf-8") == "nodefinder":
            udp_server_sock.sendto("nodeinfo".encode("utf-8"), addr)


def push_block(block, addr=None):
    """向网络广播节点"""
    data = block.__str__()
    PORT = Config.PORT
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_list_su = []
    if addr:
        address = addr
        for count in range(10):
            udp_cli_sock.sendto(bytes(data.encode('utf-8')), address)
            mesg, addr = udp_cli_sock.recvfrom(1024)
            if mesg == bytes("yishoudaoqukuai".encode('utf-8')):
                break
            else:
                time.sleep(0.1)
    else:
        ip_list = find_node()
        for ip in ip_list:
            address = (ip, PORT)
            for count in range(10):
                udp_cli_sock.sendto(bytes(data.encode('utf-8')), address)
                mesg, addr = udp_cli_sock.recvfrom(1024)
                if mesg == bytes("yishoudaoqukuai".encode('utf-8')):
                    ip_list_su.append(ip)
                    break
                else:
                    time.sleep(0.1)
    return ip_list_su


def get_max_index():
    """从全网获取最长的链的长度"""
    ip_list = find_node()
    PORT = Config.PORT
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_dict = {}
    max_ip = max(ip_dict, key=ip_dict.get)
    max_index = ip_dict["max_ip"]
    return max_ip, max_index


def sync_block_request(ip, index):
    address = (ip, Config.PORT)
    request = "QingQiuTongBuKuai"
    data = {
        "index": index
    }
    request_struct(request, data, address)


def request_struct(request, data, address, timeout=None):
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', Config.PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    data_json = {
        "request": request,     # 请求类型
        "data": data    # 发送的数据内容
    }
    response_data = None
    for count in range(10):
        udp_cli_sock.sendto(bytes(json.dumps(data_json)), address)
        mesg, addr = udp_cli_sock.recvfrom(1024)
        if timeout:
            time.sleep(timeout)
    return response_data


class Client(object):
    """UDP发送端"""
    def __init__(self):
        udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_cli_sock = udp_cli_sock
        self.addr = (Config.IPPOOL, Config.PORT)

    def _push(self, request, data, addr):
        mesg = {
            "request": request,
            "data": data
        }
        if addr:
            self.udp_cli_sock.sendto(json.dumps(mesg).encode('utf-8'), addr)
        else:
            self.udp_cli_sock.sendto(json.dumps(mesg).encode('utf-8'), self.addr)
        self.udp_cli_sock.close()

    def push_blocks(self, block_list, addr=None):
        self._push(request="chuanSongKuai", data=block_list, addr=addr)

    def sync_chain(self, index):
        self._push(request="sync", data=index)


def server():
    """UDP接收端"""
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


def send_file(path):
    """向全网广播文件"""
    addr = (Config.IPPOOL, Config.FILEPORT)
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    f = open(path, 'rb')
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
    """接收文件"""
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
            break
        udp_server_sock.sendto('ok'.encode('utf-8'), client_addr)
        count += 1
    f.close()
    udp_server_sock.close()


if __name__ == "__main__":
    find_node()

