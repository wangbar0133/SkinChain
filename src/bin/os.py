import os
import shutil
import base64

from config import Config


def copy_file(srcfile, dstpath):
    """复制文件到指定文件夹"""
    try:
        if not os.path.exists(srcfile):
            os.mkdir(dstpath)

        src_path, file_name = os.path.split(srcfile)
        shutil.copy(srcfile, dstpath + file_name)
        return True
    except:
        return False


def return_img_stream(img_local_path):
    """获取图片文件流"""
    img_stream = ''
    with open(img_local_path, 'r') as img_f:
        img_stream = img_f.read()
    img_stream = base64.b64encode(img_stream)
    return img_stream


def get_pic_path(coin):
    """获取图像绝对路径"""
    path = Config.UPLOAD_FOLDER + coin + "/"
    pic_path_dict = os.listdir(path)
    pic_path = path + pic_path_dict[0]
    return pic_path
