#-*-coding:utf-8-*-
import ztk_update
import logging
import sys

# 设置共享目录
sys.path.append("/home/uwsgi/wx_budeniao/wx_budeniao/plugin")
sys.path.append("/home/uwsgi/wx_budeniao/static")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,format = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')
    ztk_update.updateOrders()
