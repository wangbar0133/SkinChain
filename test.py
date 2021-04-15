import socket
import time
import json

if __name__ == "__main__":
    udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_sock.bind(('127.0.0.1', 9999))
    udp_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print("开启监听")
    while True:
        mesg, addr = udp_server_sock.recvfrom(1024)
        addr = ("10.65.6.202", 9999)
        udp_server_sock.sendto(bytes((json.dumps("")).encode('utf-8')), addr)
