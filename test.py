import socket
import time
import json
import ed25519

from src.user.account import Account


if __name__ == "__main__":
    username, password = Account().create_account()
    print(username)
    print(password)