# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import requests
import json

# 下面是正式生产账号
appid = 'wx58c5278a0d5d14cc'
secret = 'b11dc12700227e639615acdc6f2dae62'

# 测试账号
# appid = "wx1ea8d60ec91fc103"
# secret = "1b90e79442b7b0cb5033839e58922399"


def wxtoken():  # 返回有效的access_token
    f = open('access_token.txt', 'r')
    access_token = f.read()
    f.close()
    return access_token.strip()


def get_access_token():  # 被动获取 通过函数直接获取
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    text_mod = {'appid': appid, 'secret': secret, 'grant_type': 'client_credential'}
    db_res = requests.get(url, params=text_mod)
    # print(res.text)
    access_token_req = json.loads(db_res.text)
    return access_token_req['access_token']


def get_user():
    url = "https://api.weixin.qq.com/cgi-bin/user/get"
    access_token = wxtoken()
    params = {"access_token": access_token}
    req = requests.get(url, params)
    req.encoding = "utf-8"
    return req.text


def get_user_detail_info(my_openid, lang="zh_CN"):  # 获得微信用户详细信息
    url = "https://api.weixin.qq.com/cgi-bin/user/info"
    access_token = wxtoken()
    params = {"access_token": access_token, "openid": my_openid, "lang": lang}
    req = requests.get(url, params)
    req.encoding = "utf-8"
    return req.text


def get_user_info_batch(user_list):
    url = "https://api.weixin.qq.com/cgi-bin/user/info/batchget?access_token=%s" % wxtoken()
    params = {"user_list": user_list}
    post_data = json.dumps(params)
    req = requests.post(url, post_data)
    req.encoding = "utf-8"
    return req.text


def oauth2_code(code):
    url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {"appid": appid,
              "secret": secret,
              "code": code,
              "grant_type": "authorization_code"}
    req = requests.get(url, params)
    req.encoding = "utf-8"
    return req.text


def qrcode(my_openid):  # 获得邀请二维码
    req_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s' % wxtoken()
    # print(req_url)
    params = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": my_openid}}}
    post_data = json.dumps(params)
    req = requests.post(req_url, post_data)
    req.encoding = "utf-8"
    # print(req.text)
    json_data = json.loads(req.text)
    return json_data['url']


def check_openid(my_openid):
    if len(my_openid) != 28:
        return None
    db_res = get_user_detail_info(my_openid)
    return db_res


def get_all_private_template():
    req_url = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template"
    access_token = wxtoken()
    params = {"access_token": access_token}
    db_res = requests.get(req_url, params)
    return db_res.text


def cli(my_text):  # 返回草料二维码
    req_url = 'https://cli.im/api/qrcode/code'
    params = {'text': my_text, 'mhid': 'sELPDFnok80gPHovKdI'}
    db_res = requests.get(req_url, params)
    soup = BeautifulSoup(db_res.text, 'html.parser')  # html.parser为内置html解释器
    qrcodeurl = 'http:' + soup.img.attrs['src']
    return qrcodeurl


# 通过openid获得草料二维码的图片地址
def getqrcode(my_openid):
    return cli(qrcode(my_openid))


def orderSuccess(to_user, order, level_coefficient):  # 通过客服消息成功发送订单信息
    item_title = order['item_title']
    trade_id = str(order['trade_id'])
    alipay_total_price = str(round(float(order['alipay_total_price']), 2))
    pub_share_pre_fee = str(round(float(order['pub_share_pre_fee']) * level_coefficient, 2))
    content = '———下单成功———\n'
    content = content + item_title + '\n'
    content = content + '订单编号：\n'
    content = content + trade_id + '\n'
    content = content + '[红包]实付：' + alipay_total_price + '\n'
    content = content + '[红包]红包：' + pub_share_pre_fee + '\n'
    content = content + '——————————\n'
    content = content + '下单成功，请确认收货第二天后找我拿红包拿来，如果小主觉得我好用，请推荐给朋友哦！'
    return customTextSend(to_user, content)


def orderInfo(toUser, order, level_coefficient):  # 通过客服消息发送订单信息
    item_title = order['item_title']
    trade_id = str(order['trade_id'])
    alipay_total_price = str(round(float(order['alipay_total_price']), 2))
    pub_share_pre_fee = str(round(float(order['pub_share_pre_fee']) * level_coefficient, 2))
    content = '———订单查询———\n'
    content = content + item_title + '\n'
    content = content + '订单编号：\n'
    content = content + trade_id + '\n'
    content = content + '[红包]实付：' + alipay_total_price + '\n'
    content = content + '[红包]红包：' + pub_share_pre_fee + '\n'
    content = content + '——————————\n'
    content = content + '订单查询成功，如果小主觉得我好用，请推荐给朋友哦！'
    return customTextSend(toUser, content)


def customTextSend(toUser, text):  # 发送客服消息,注意条件限制，否则会发送失败
    accesstoken = wxtoken()
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' % accesstoken
    postdata = {
        "touser": toUser,
        "msgtype": "text",
        "text": {
            "content": text
        }
    }
    postdata = json.dumps(postdata, ensure_ascii=False).encode('utf-8')
    req = requests.post(url, postdata)
    return json.loads(req.text)


def templateMsgSend(toUser, first, nick, bindingtime, my_text, remark):  # 发送模板消息
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % (wxtoken())
    postdata = {
        "touser": toUser,
        "template_id": "gx-WFRNpRw7RR9HBV-lSpPP13h5gdRwPXc-AK5lffac",
        "data": {
            "first": {
                "value": first,
                "color": "#173177"
            },
            "keyword1": {
                "value": nick,
                "color": "#173177"
            },
            "keyword2": {
                "value": bindingtime,
                "color": "#173177"
            },
            "keyword3": {
                "value": my_text,
                "color": "#173177"
            },
            "remark": {
                "value": remark,
                "color": "#173177"
            }
        }
    }
    postdata = json.dumps(postdata)
    req = requests.post(url, postdata)
    jsondata = json.loads(req.text)
    return jsondata


if __name__ == "__main__":
    text = "测试"
    openid = "o1mDH1HT8Nf7EdDc2-WJbw8mXkvk"
    res = get_access_token()
    print(res)
