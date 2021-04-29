# -*-coding:utf-8-*-
import base64
import os
import shutil
import hashlib

from config import Config
from src.bin.log import Log


def move_file(srcfile, dstpath):
    """复制文件到指定文件夹"""
    try:
        if not os.path.exists(dstpath):
            os.mkdir(dstpath)
        shutil.move(srcfile, dstpath)
        return True
    except Exception as e:
        Log().error("文件不存在：" + str(e))
        print("文件不存在：" + str(e))
        return False


def return_img_stream(img_local_path):
    """获取图片文件流"""
    img_stream = ''
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
    img_stream = base64.b64encode(img_stream)
    return img_stream


def file_hash(file_path):
    """对文件取哈希值"""
    byte = 1024
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(byte)
            if data:
                md5.update(data)
            else:
                break
    return md5.hexdigest()


def get_pic_path(coin):
    """获取图像绝对路径"""
    path = Config.UPLOAD_FOLDER + coin
    pic_path_dict = os.listdir(path)
    if pic_path_dict[0]:
        pic_path = path + "\\" + pic_path_dict[0]
        if coin == file_hash(pic_path):
            return pic_path
        else:
            return Config.FILe_ERROR
    else:
        return Config.FILe_ERROR


if __name__ == "__main__":
    srcfile = "C:\\Users\\Administrator.DESKTOP-35V3OQH\\SkinChain\\static\\images\coins\\temp\\wallhaven-ymz61d.jpg"
    dstpath = "C:\\Users\\Administrator.DESKTOP-35V3OQH\\SkinChain\\static\\images\coins\\97b2071a7dc8a39518b560e4f95969e3\\"
    move_file(srcfile, dstpath)
