# -*- coding:utf8 -*-
import weixin
import sys

def write_wxtoken(access_token):
    f = open('access_token.txt', 'w') 
    f.write(access_token)   
    f.close()                                                             

if __name__ == "__main__":
    # 设置共享目录
    sys.path.append("/home/uwsgi/wx_budeniao/wx_budeniao/plugin")
    sys.path.append("/home/uwsgi/wx_budeniao/static")
    write_wxtoken(weixin.get_access_token())
