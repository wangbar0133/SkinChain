import socket
import time
import json

from config import Config


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
            self.udp_cli_sock.sendto(json.dumps(mesg).encode('utf-8'), addr)
        else:
            self.udp_cli_sock.sendto(json.dumps(mesg).encode('utf-8'), self.addr)
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
