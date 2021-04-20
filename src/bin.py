import os
import shutil


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