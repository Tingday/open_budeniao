# 主程序文件 view.py
import json
import wx_budeniao.plugin.linksql as lks
import wx_budeniao.plugin.weixin as wx
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


# 主页
def index(request):
    return HttpResponse("后台系统正常运行中。")


# 所有订单
def orders(request):
    request.encoding = "utf-8"
    context = {}
    db_res = lks.new_orders()
    # user_name = lks.user_info_by_openid()
    output_orders = []
    for order in db_res:  # 遍历修改状态，修改用户名
        if order["tk_status"] == "3":
            order["tk_status"] = "订单结算"
        elif order["tk_status"] == "14":
            order["tk_status"] = "订单成功"
        elif order["tk_status"] == "12":
            order["tk_status"] = "订单付款"
        elif order["tk_status"] == "13":
            order["tk_status"] = "订单失败"
        else:
            pass  # 维持订单数字表达意思
        tk_user = lks.user_info_by_openid(order["openid"])[0]
        order["user_name"] = tk_user["xingming"]
        output_orders.append(order)
    # print(output_orders)
    context["orders"] = output_orders
    context["title"] = "所有订单"
    return render(request, "orders.html", context)


# 查询订单
def get_order(request):
    request.encoding = "utf-8"
    context = {}
    if "keys" in request.GET and request.GET['keys']:
        trade_id = request.GET['keys']
        db_res = lks.getOrderPlus(trade_id)
        # print(db_res)
        if db_res:
            title = "订单详情"
            context["orders"] = db_res
            context["title"] = title
            return render(request, "orders.html", context)
        else:
            return HttpResponse("未找到订单。")
    else:
        return HttpResponse("请输入订单号。")


# 绑定支付宝
def bind_alipay(request):
    request.encoding = "utf-8"
    context = {}
    if "code" in request.GET and request.GET['code']:
        code = request.GET['code']
        wx_res = json.loads(wx.oauth2_code(code))
        # print(wx_res)
        if "openid" in wx_res:
            openid = wx_res['openid']
            context['openid'] = openid
            context['title'] = "绑定支付宝"
            return render(request, "bind_alipay.html", context)
        else:
            return HttpResponse("网页已过期！")
    else:
        return HttpResponse("请使用微信打开！")


# 绑定支付宝 by openid
def bind_alipay_by_openid(request):
    request.encoding = "utf-8"
    context = {}
    if "openid" in request.GET and request.GET['openid']:
        openid = request.GET['openid']
        context["openid"] = openid
        context["title"] = "绑定支付宝"
        return render(request, "bind_alipay.html", context)
    else:
        return HttpResponse("网页已过期！")


# 用户列表
def user_list(request):
    request.encoding = "utf-8"
    context = {}
    if "page" in request.GET and request.GET['page']:
        page = request.GET['page']
        db_res = lks.user_list(page=page)
    else:
        db_res = lks.user_list()
    user_list_res = db_res
    title = "所有用户"
    context["title"] = title
    context["user_list"] = user_list_res
    #    print(db_res)
    return render(request, "user_list.html", context)


# 提现中
def cashing(request):
    context = {}
    db_res = lks.cash_now()
    # print(db_res)
    if db_res:
        context["title"] = "提现中"
        context["user_list"] = db_res
        return render(request, "cashing.html", context)
    else:
        return HttpResponse("没有提现中")


#
if __name__ == "__main__":
    print(user_list())


# 用户个人中心
def user_info(request):
    request.encoding = "utf-8"
    context = {}
    if "openid" in request.GET and request.GET['openid']:
        openid = request.GET['openid']
        # 更新信息
        update_res = lks.updateUser(openid)
        # print(update_res)
        res = lks.user_info_by_openid(openid)
    else:
        res = {"message": "请输入用户id", "code": "-1"}
    return JsonResponse(res, safe=False)
