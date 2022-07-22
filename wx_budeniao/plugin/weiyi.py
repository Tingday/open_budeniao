# -*- coding: utf-8 -*-
# filename: weiyi.py 
import json
import requests

_sys_vekey = "V00001220Y06069594"


def sys_remain():
    url = "http://api.vephp.com/remain"
    textmod = {"vekey": _sys_vekey}
    res = requests.get(url=url, params=textmod)
    jsondata = json.loads(res.text)
    return jsondata


def hcapi(para, mmpid, relationId=None):
    url = 'http://gfapi.vephp.com/hcapi'
    if relationId:  # 存在rid
        textmod = {'vekey': _sys_vekey, 'detail': '1', 'para': para, 'pid': mmpid, 'relationId': relationId,
                   'tkl_type': '0'}
    else:
        textmod = {'vekey': _sys_vekey, 'detail': '1', 'para': para, 'pid': mmpid, 'tkl_type': '0'}
    res = requests.get(url=url, params=textmod)
    json_res = json.loads(res.text)
    # print(json_res)
    return json_res


def publishertkl(rtag):  # 会员渠道备案
    url = 'http://gfapi.vephp.com/publishertkl'
    textmod = {'vekey': 'V00001220Y06069594', 'inviter_code': 'RJXRMQ', 'rtag': rtag,
               'text': '不得鸟会员备案'}  # rtag = openid
    res = requests.get(url=url, params=textmod)
    jsondata = json.loads(res.text)
    return jsondata


def publisherget(relationId=None, page=1, pagesize=10):  # 轮讯渠道信息
    url = 'http://gfapi.vephp.com/publisherget'
    if relationId:
        textmod = {'vekey': 'V00001220Y06069594', 'relationId': relationId, 'page': page, 'pagesize': pagesize}
    else:
        textmod = {'vekey': 'V00001220Y06069594', 'page': page, 'pagesize': pagesize}
    res = requests.get(url=url, params=textmod)
    jsondata = json.loads(res.text)
    return jsondata


def tbkorder(start_time, order_scene=1):  # 订单查询 20分钟订单
    url = 'http://gfapiorder.vephp.com/order'
    textmod = {'vekey': 'V00001220Y06069594', 'start_time': start_time, 'order_scene': order_scene, 'span': 60}
    res = requests.get(url=url, params=textmod)
    json_res = json.loads(res.text)
    if json_res['data'] and json_res['error'] == '0':
        return json_res['data']
    else:
        return json_res['msg']


def products(topcat='热销', subcate='女装', page=1, pagesize=10, sort='tk_rate_des'):  # 热销高佣商品
    url = 'http://tmp.vephp.com/products'
    textmod = {
        'vekey': 'V00001220Y06069594',
        'topcat': topcat,
        'subcate': subcate,
        'page': page,
        'pagesize': pagesize,
        'sort': sort
    }
    res = requests.get(url=url, params=textmod)
    jsondata = json.loads(res.text)
    return jsondata


if __name__ == "__main__":
    print(sys_remain())
