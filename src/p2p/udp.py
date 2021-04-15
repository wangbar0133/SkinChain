import socket
import time
import json


def get_host_ip():
    """返回本机IP地址"""
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ss.connect(('8.8.8.8', 8070))
        ip = ss.getsockname()[0]
    finally:
        ss.close()
    return ip


def find_node():
    PORT = 9999
    ip_pool = "192.168.0.255"
    address = (ip_pool, PORT) 
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    ip_list = []
    for i in range(100):
        udp_cli_sock.sendto(bytes("".encode('utf-8')), address)
        mesg, addr = udp_cli_sock.recvfrom(1024)
        ip_list.append(addr)

    ip_list = set(ip_list)

    return ip_list


def call_back():
    """查找结点时回信"""
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind(('127.0.0.1', 9999))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        udp_server_sock.sendto(bytes("".encode('utf-8')), addr)


def push_block(block):
    data = block.__str__()
    PORT = 9999
    ip_pool = "192.168.0.255"
    address = (ip_pool, PORT)
    udp_cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_sock.bind(('', PORT))
    udp_cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)







if __name__ == "__main__":
    find_node()

