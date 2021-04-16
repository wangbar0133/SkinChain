import socket
import time
import json

from config import Config
from ..block_chain.block import check_block, BlockChain


def get_host_ip():
    """返回本机IP地址"""
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(('8.8.8.8', 8070))
    ip = ss.getsockname()[0]
    ss.close()
    return ip


def find_node():
    """查找网络上的节点"""
    PORT = Config.PORT
    ip_pool = Config.IPPOOL
    address = (ip_pool, PORT) 
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_list = []
    for count in range(100):
        udp_cli_sock.sendto(bytes("nodefinder".encode('utf-8')), address)
        mesg, addr = udp_cli_sock.recvfrom(1024)
        ip_list.append(addr)
    ip_list = set(ip_list)
    return ip_list


def udp_listen():
    """监听UDP请求"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind((get_host_ip(), Config.PORT))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        if mesg == bytes("nodefinder".encode('utf-8')):
            udp_server_sock.sendto(bytes("".encode('utf-8')), addr)
        elif bytes("tongbuqingqiu".encode('utf-8')) in mesg:
            data = str(mesg, encoding="utf-8")
            data = json.loads(data)
            index = data["index"]
            sync_block_response(addr, index)
        else:
            block = str(mesg, encoding="utf-8")
            if check_block(block):
                for i in range(10):
                    if BlockChain().insert_block(block):
                        udp_server_sock.sendto(bytes("yishoudaoqukuai".encode('utf-8')), addr)
                        break


def push_block(block):
    """向网络广播节点"""
    data = block.__str__()
    PORT = Config.PORT
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ip_list = find_node()
    ip_list_su = []
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
    for ip in ip_list:
        address = (ip, PORT)
        request = "QingQiuZuiDaChangDu"
        response = "YiShouDaoZuiDaChangDuQingQiu"
        data = ""
        response_data = request_struct(request, response, data, address, timeout=0.1)

        ip_dict[ip] = response_data["index"]

        address = (ip, PORT)
        for count in range(10):
            udp_cli_sock.sendto(bytes("qingqiuzuixinkuai".encode('utf-8')), address)
            mesg, addr = udp_cli_sock.recvfrom(1024)
            if mesg:
                ip_dict[ip] = ip_dict[ip] + 1 if ip in ip_dict else 1
                break
            else:
                time.sleep(0.1)
    max_ip = max(ip_dict, key=ip_dict.get)
    max_index = ip_dict["max_ip"]
    return max_ip, max_index


def sync_block_request(ip, index):
    address = (ip, Config.PORT)
    request = "QingQiuTongBuKuai"
    response = "YiShouDaoTongBuQingQiu"
    data = {
        "index": index
    }
    request_struct(request, response, data, address)


def sync_block_response(address, index_list):
    for index in index_list:
        block = BlockChain().get_block_by_index(index)
        request = "FaSongKuai"
        response = "YiShouDaoKuai"
        data = block
        request_struct(request, response, data, address)


def request_struct(request, response, data, address, timeout=None):
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
        resp = str(mesg, encoding="utf-8")
        resp = json.loads(resp)
        if resp["request"] == response:
            response_data = resp["data"]
            break
        if timeout:
            time.sleep(timeout)
    return response_data


if __name__ == "__main__":
    find_node()

