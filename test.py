import socket
import threading
import time
import json
import ed25519
import os
from config import Config
import pymongo
import requests
from threading import Thread
from time import sleep, ctime
import os
import pexpect
import datetime


def ping_all(ip_pool):
    ip_list = list()
    for ip in ip_pool:
        cmd = "ping -n 1 " + ip + '|findstr TTL'
        res = os.popen(cmd)
        if res.readlines():
            ip_list.append(ip)
    return ip_list


def test_db(ip):
    try:
        myclient = pymongo.MongoClient(host=ip, port=27017, serverSelectionTimeoutMS=50, socketTimeoutMS=50)
        dblist = myclient.list_database_names
    except:
        pass


def ping(ip):
    cmd = "ping -n 1 " + ip + '|findstr TTL'
    res = os.popen(cmd)
    if res.readlines():
        ip_alive_list.append(ip)


def ping_mongod(ip):
    try:
        myclient = pymongo.MongoClient(host=ip, port=27017, serverSelectionTimeoutMS=50, socketTimeoutMS=50)
        dblist = myclient.list_database_names()
        if dblist:
            ip_list.append(ip)
    except:
        pass


if __name__ == "__main__":
    IPPOOL = "192.168.0.255"
    conf = IPPOOL.split(".")
    ip_prefix = ""
    for count in range(0, 3):
        if conf[count] != "255":
            ip_prefix = ip_prefix + conf[count] + "."

    ip_pool = list()
    for count in range(1, 255):
        ip_pool.append(ip_prefix + str(count))

    ip_alive_list = list()

    thread_list = list()

    for ip in ip_pool:
        thread_list.append(threading.Thread(target=ping, args=(ip,)))

    for thread in thread_list:
        thread.start()


    thread_mongod_list = list()

    for ip in ip_alive_list:
        thread_mongod_list.append(threading.Thread(target=ping_mongod, args=(ip,)))

    ip_list = list()

    for thread in thread_mongod_list:
        thread.start()

    for thread in thread_mongod_list:
        thread.join()

    print(ip_list)

    # myclient = pymongo.MongoClient(host="192.168.0.14", port=27017, serverSelectionTimeoutMS=50, socketTimeoutMS=50)
    # dblist = myclient.list_database_names()
    # print(dblist)
    pass
