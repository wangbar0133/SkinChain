# -*-coding:utf-8-*-
import base64
import os
import shutil

from config import Config
from src.bin.log import Log


def move_file(srcfile, dstpath):
    """复制文件到指定文件夹"""
    try:
        if not os.path.exists(dstpath):
            os.mkdir(dstpath)
        if os.path.exists(srcfile):
            return True
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


def get_pic_path(coin):
    """获取图像绝对路径"""
    path = Config.UPLOAD_FOLDER + coin
    pic_path_dict = os.listdir(path)
    pic_path = path + "\\" + pic_path_dict[0]
    return pic_path


if __name__ == "__main__":
    coin = "fc503153dab068850d83a3e7dbb88585"
    print(return_img_stream(get_pic_path(coin)))
    pass
