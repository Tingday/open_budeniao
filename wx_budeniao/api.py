# 这是控制函数 api 注意区别view界面

import json
import wx_budeniao.plugin.linksql as lks
import wx_budeniao.plugin.weixin as wx
import wx_budeniao.plugin.process as pcs  # 主程序
from django.shortcuts import render
from django.http import HttpResponse
import hashlib
from django.http import JsonResponse


def alipay(request):
    context = {}
    if "zhifubao" in request.GET and request.GET["zhifubao"]:
        phonenumber = request.GET["zhifubao"]
        xingming = request.GET["xingming"]
        openid = request.GET["openid"]
        bind_res = lks.alipay(phonenumber, xingming, openid)
        if bind_res:
            context = {"title": "绑定成功！", "message": "绑定成功，请返回微信界面进行提现操作。"}
            return render(request, "msg.html", context)
        else:
            context = {"title": "绑定失败！", "message": "绑定失败，不允许重复绑定，请联系客服管理员。"}
            return render(request, "msg.html", context)
    else:
        context = {"title": "运行中", "message": "网站正常运行中..."}
        return render(request, "msg.html", context)


# 提现
def tixian(request):
    request.encoding = "utf-8"
    context = {}
    if 'openid' in request.GET and request.GET['openid']:
        openid = request.GET['openid']
        lks_res = lks.iscashing(openid)
    else:
        return HttpResponse("请联系管理员！")
    if lks_res:
        lks_res_msg = lks.cash(openid)  # 提现
        if lks_res_msg:
            return HttpResponse("提现成功！")
        else:
            return HttpResponse("提现失败，请联系管理员！\n 微信：939179162")
    else:
        return HttpResponse("用户未申请提现。")


# 微信主程序
def wx(request):
    if request.method == "POST":
        res = pcs.wx_post(request.body)
        return res
    else:
        webinput = request.GET
        if len(webinput) == 0:
            return HttpResponse("微信公众号服务器正常运行中。。。")
        signature = webinput["signature"]
        timestamp = webinput["timestamp"]
        nonce = webinput["nonce"]
        echostr = webinput["echostr"]
        token = 'test'  # 和公众号上设置的一致
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update(list[0].encode("utf-8"))
        sha1.update(list[1].encode("utf-8"))
        sha1.update(list[2].encode("utf-8"))
        # map(sha1.update, list)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return HttpResponse(echostr)
        else:
            return None
