# -*- coding: utf-8 -*-
import random
import time
import sms
import reply
import receive
import weiyi
import linksql
import json
import banwords
import weixin
from django.http import HttpResponse
import logging


def wx_post(request):
    webData = request
    recMsg = receive.parse_xml(webData)
    toUser = recMsg.FromUserName
    fromUser = recMsg.ToUserName
    openid = recMsg.FromUserName
    # todo 需要判定用户是否存在
    linksql.updateUser(openid)  # 事件钩子，更新用户信息
    # 以下为文本回复界面；
    # 以后将不再支持通过指令回复，因为微信公众号的菜单功能支持了
    if isinstance(recMsg, receive.Msg) and recMsg.MsgType == "text":
        recContent = recMsg.Content.decode("utf-8")  # utf-8编码
        # 分配pid 此处应省略，然后在各处添加要求绑定渠道的信息 此处暂时无法删除是因为非渠道模式需要主动分配pid来临时识别用户。
        # 除非强制要求用户绑定渠道，而且必须每月下一单。这个比较困难。
        linksql.new_pid(openid)
        sql_res = linksql.user_info_by_openid(openid)
        if sql_res:
            user_info = sql_res[0]
        else:
            sql_res = linksql.create_new_user(openid)
            user_info = sql_res[0]  # 创建的新用户
        if recContent == "提现":
            return HttpResponse(tixian(user_info, openid, toUser, fromUser), content_type="text/xml")
        elif recContent == "会员备案":
            if not (linksql.publisher(openid)):
                logging.info(openid + " 会员备案")
                webdata = weiyi.publishertkl(openid)
                if webdata["error"] == "0":
                    content = "复制本淘口令打开手机淘宝进行会员备案\n%s\n\n提示:成功备案第二天即可使用机器人哦！" % (
                        webdata["tbk_pwd"]
                    )
                else:
                    content = "淘口令生成失败请联系客服"
            else:
                content = "你已经备案了,无需重复备案。"
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recContent == "邀请码":
            logging.info(openid + " 邀请码")
            qrcodeurl = weixin.getqrcode(openid)
            content = '<a href="%s">点击这里查看你的专属邀请码</a>\n' % qrcodeurl
            content = content + "通过该邀请码关注公众号的均为你的代理，你可以获得他的18%返利，赶紧推荐给更多人吧！"
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recContent == "查询":
            return HttpResponse(userinfo(user_info, toUser, fromUser), content_type="text/xml")
        elif recContent == "帮助":
            content = (
                "———系统提示———\n"
                "发送“签到”每天领取小额红包\n"
                "发送“查询”可以查询个人信息\n"
                "发送“提现”可以提取当前余额\n"
                "发送“帮助”可以查看相关指令\n"
                "如有其它问题请加客服微信解决\n"
            )
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recContent == "签到":
            return HttpResponse(qiandao(user_info, toUser, fromUser), content_type="text/xml")
        elif recContent == "openid":
            content = openid
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recContent == "appid":
            content = fromUser
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recContent.isdigit() and len(recContent) == 19:  # 淘宝订单号
            sqlorder = linksql.getorder(openid, recContent)
            if openid == "o1mDH1HT8Nf7EdDc2-WJbw8mXkvk":
                sqlorder = linksql.getOrderPlus(recContent)
            if sqlorder:

                weixin.orderInfo(openid, sqlorder[0],
                                 user_info["level_coefficient"])
                logging.info(openid + " 订单查询成功")
                return HttpResponse("success")
            else:
                content = "订单查询失败"
                logging.info(openid + " 订单查询失败" + recContent)
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return HttpResponse(replyMsg.send(), content_type="text/xml")
        else:
            if linksql.publisher(openid):
                mmpid = "mm_32003052_325200030_101473650037"  # rid模式通用pid
                relation_id = linksql.publisher(openid)
                webdata = weiyi.hcapi(recContent, mmpid, relation_id)
            elif linksql.openidpid(openid):  # pid模式
                mmpid = "mm_32003052_324300396_" + \
                        str(linksql.openidpid(openid))
                webdata = weiyi.hcapi(recContent, mmpid)
            else:  # 关系不存在，可能是pid关系库满了，也可能是bug
                logging.info(openid + " pid bug error!")
                # sms.smssql("关系不存在，可能是pid关系库满 process.py")
                print("紧急关系处理")
                return HttpResponse("success")
            # print("webdata的长度：",len(webdata))
            logging.info(openid + " 查询返利")
            # logging.info("webdata", webdata)
            if "result" in webdata and webdata['result'] == 1:  # 有优惠券
                towords = webdata['data']['tbk_pwd'].replace("￥", "")
                index_jian = webdata['data']['coupon_info'].find("减")
                index_yuan = webdata['data']['coupon_info'].find("元", index_jian)
                quan = str(
                    webdata['data']['coupon_info'][index_jian + 1: index_yuan])  # 优惠券额度
                title = banwords.nobantext(webdata['data']['title'])
                replyMsg = reply.NewsMsg(
                    toUser,
                    fromUser,
                    "约返:"
                    + str(
                        round(
                            float(webdata['data']['commission_rate'])
                            * 0.01
                            * user_info["level_coefficient"]
                            * (float(webdata['data']['zk_final_price']) - float(quan)),
                            2,
                        )
                    )
                    + " 优惠券:"
                    + quan
                    + " 付费价:"
                    + str(float(webdata['data']['zk_final_price']) - float(quan)),
                    title,
                    webdata['data']['pict_url'],
                    "https://budeniao.net/pwd/index.html?taowords="
                    + towords
                    + "&url="
                    + webdata['data']['coupon_short_url']
                    + "&image="
                    + webdata['data']['pict_url'],
                )
                return HttpResponse(replyMsg.send(), content_type="text/xml")
            elif "result" in webdata and webdata['result'] == 2:  # 无优惠券
                towords = webdata['data']['tbk_pwd'].replace("￥", "")
                title = banwords.nobantext(webdata['data']['title'])
                replyMsg = reply.NewsMsg(
                    toUser,
                    fromUser,
                    "约返:"
                    + str(
                        round(
                            float(webdata['data']['commission_rate'])
                            * 0.01
                            * user_info["level_coefficient"]
                            * float(webdata['data']['zk_final_price']),
                            2,
                        )
                    )
                    + " 优惠券:0"
                    + " 付费价:"
                    + webdata['data']['zk_final_price'],
                    title,
                    webdata['data']['pict_url'],
                    "https://budeniao.net/pwd/index.html?taowords="
                    + towords
                    + "&url="
                    + webdata['data']['coupon_short_url']
                    + "&image="
                    + webdata['data']['pict_url'],
                )
                return HttpResponse(replyMsg.send(), content_type="text/xml")
            else:  # 非产品ID、或淘口令，或淘客链
                content = "———系统消息———\n" + webdata['msg']
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return HttpResponse(replyMsg.send(), content_type="text/xml")

    # 以下为菜单事件系统
    elif isinstance(recMsg, receive.Msg) and recMsg.MsgType == "event":
        recEvent = recMsg.Event
        sql_res = linksql.user_info_by_openid(openid)  # 获取用户信息对象，失败时创建新用户
        if sql_res:
            user_info = sql_res[0]
        else:
            sql_res = linksql.create_new_user(openid)
            user_info = sql_res[0]  # 创建的新用户
        if recEvent == "subscribe":  # 关注公众号
            EventKey = recMsg.EventKey
            if EventKey:  # 有代理参数
                scene = EventKey.split("_")
                proxy = scene[1]  # s设置代理
                if linksql.setProxy(openid, proxy):
                    weixin.customTextSend(openid, "邀请成功！")
                    logging.info(openid + " 设置代理")
                else:
                    weixin.customTextSend(openid, "你已经是代理会员了哦！")
            text = "欢迎关注不得鸟优惠券。\n 你可以点击下方菜单使用教程了解更多哦！"
            webdata = weiyi.publishertkl(openid)
            content = "首次使用需绑定淘宝哦！\n请复制这段文字后打开手机淘宝进行绑定。\n" + webdata["tbk_pwd"]
            weixin.customTextSend(openid, text)  # 这个是欢迎信息
            replyMsg = reply.TextMsg(toUser, fromUser, content)  # 发送淘宝绑定信息
            return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recEvent == "CLICK":  # 点击菜单按钮
            recEventKey = recMsg.EventKey
            if recEventKey == "V1001_QIANDAO":  # 签到
                return HttpResponse(qiandao(user_info, toUser, fromUser), content_type="text/xml")
            elif recEventKey == "V1001_YAOQING":  # 邀请码
                logging.info(openid + " 邀请码")
                qrcodeurl = weixin.getqrcode(openid)
                content = '<a href = "%s">点击你的专属邀请码</a>\n' % qrcodeurl
                content = content + "邀请码好友关注公众号，你可以获得他的18%返利，赶紧分享给更多人吧!"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return HttpResponse(replyMsg.send(), content_type="text/xml")
            elif recEventKey == "V1001_JIAOCHENG":  # 教程
                title = "省钱购物，必看教程"
                description = "第一步：点击标题后面的“分享有奖”"
                picUrl = "https://budeniao.net/logo.jpg"
                url = "https://t.cn/EIfL66p"
                logging.info(openid + " 查看教程")
                replyMsg = reply.NewsMsg(
                    toUser, fromUser, title, description, picUrl, url
                )
                return HttpResponse(replyMsg.send(), content_type="text/xml")
            elif recEventKey == "V1001_ALIPAY":  # 绑定支付宝
                # todo 完成支付宝绑定前检查
                print(user_info)
                if user_info["alipay"]:
                    content = "账户无需重复绑定，修改请联系客服。"
                    replyMsg = reply.TextMsg(toUser, fromUser, content)  # 发送淘宝绑定信息
                    return HttpResponse(replyMsg.send(), content_type="text/xml")
                else:
                    title = "绑定支付宝"
                    description = "绑定支付宝，快速无门槛提现红包返利。"
                    picUrl = "https://budeniao.net/alipay.jpg"
                    url = "https://wx.budeniao.net/bind_alipay_openid?openid=" + openid
                    logging.info(openid + "绑定支付宝")
                    replyMsg = reply.NewsMsg(
                        toUser, fromUser, title, description, picUrl, url
                    )
                    return HttpResponse(replyMsg.send(), content_type="text/xml")
            elif recEventKey == "V1001_USER":  # 用户中心
                return HttpResponse(userinfo(user_info, toUser, fromUser), content_type="text/xml")
            elif recEventKey == "V1001_TIXIAN":  # 提现申请
                return HttpResponse(tixian(user_info, openid, toUser, fromUser), content_type="text/xml")
            elif recEventKey == "V1001_KEFU":
                logging.info(openid + " 联系客服")
                content = "微信号：939179162;\n电话：13590060134"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return HttpResponse(replyMsg.send(), content_type="text/xml")
        elif recEvent == "SCAN":
            content = "请分享给其他人关注哦！"
            return HttpResponse(reply.TextMsg(toUser, fromUser, content).send(), content_type="text/xml")
        else:
            logging.info(openid + " 该事件未处理：" + recEvent)
            return HttpResponse("success")
    else:  # 非文本消息
        return HttpResponse("success")


def qiandao(user_info, toUser, fromUser):
    lastdate = user_info["lastdate"]
    nowdate = time.strftime("%Y-%m-%d", time.localtime())
    if lastdate == nowdate:
        content = "你今天已经签到了"
    else:
        qian = float(random.random()) * 0.12
        logging.info(user_info["openid"] + " 签到：" + str(round(qian, 2)))
        linksql.qiandao(user_info["openid"], qian)
        content = (
                "———签到成功———\n"
                "【签到额度随机，非固定】\n"
                "本次签到获得%s元\n"
                "可提现金额：%s元\n"
                "———————————\n"
                "发淘宝商品链接给我赚返利！[红包][红包]\n"
                "如有疑问请回复【帮助】查询"
                % (str(round(qian, 2)), str(round(user_info["remain"] + qian, 2)))
        )
    replyMsg = reply.TextMsg(toUser, fromUser, content)
    return replyMsg.send()


def userinfo(user_info, toUser, fromUser):
    logging.info(user_info["openid"] + " 查询账户")
    content = "———个人帐户———\n"
    content = content + "已提现金额：%s元\n" % (str(round(user_info["cashed"], 2)))
    content = content + "可提现余额：%s元\n" % (str(round(user_info["remain"], 2)))
    content = content + "未收货金额：%s元\n" % (str(round(user_info["goods"], 2)))
    content = content + "总订单数：%s单\n\n" % (str(user_info["orders"]))
    content = content + "提现中：%s元\n" % (str(round(user_info["cash"], 2)))
    if int(user_info["num"]) > 0:
        content = content + "代理数：%d位\n" % (int(user_info["num"]))
        content = content + "推荐奖励：%s元\n" % (round(user_info["proxy_money"], 2))
        content = content + "推荐奖励尚在测试中，暂时不能提现。\n"
    content = content + "\n提示：大于5元即可提现如需提现，请回复“提现”\n"
    content = content + "[玫瑰]不要忘记置顶我哦！"
    replyMsg = reply.TextMsg(toUser, fromUser, content)
    return replyMsg.send()


def tixian(user_info, openid, toUser, fromUser):
    if user_info["remain"] < 5:
        content = (
                "———申请失败———\n你现在余额:" +
                str(round(user_info["remain"], 2)) + "元尚不能提现\n\n"
        )
        content = content + "亲，可以发送“查询”两个字，查询账户"
        logging.info(openid + " 余额不足提现")
        return reply.TextMsg(toUser, fromUser, content).send()
    if user_info["cash"] > 0:  # 避免重复提现
        content = "你还有一笔提现等待系统完成。"
        logging.info(openid + " 重复提现")
        return reply.TextMsg(toUser, fromUser, content).send()
    if not (linksql.checkalipay(openid)):
        content = "第一次提现请绑定支付宝收款账号"
        logging.info(openid + " 支付宝未绑定")
        return reply.TextMsg(toUser, fromUser, content).send()
    if not (linksql.checktixian(openid)):
        content = "下单获得的红包不足5元，暂时无法提现。\n记得多用不得鸟下单哦！"
        logging.warning(openid + " 不符合提现条件")
        return reply.TextMsg(toUser, fromUser, content).send()
    m = sms.smsTiXian(
        openid[11:],
        str(round(user_info["remain"], 2)),
        user_info["alipay"],
        user_info["xingming"],
    )
    jsData = json.loads(m)
    if jsData["Message"] == "OK":
        logging.info(openid + " 申请提现成功")
        linksql.tixian(openid)
        content = "———申请成功———\n"
        content = content + "本次提现%s元\n系统将会把钱发送到你的支付宝中\n\n24小时内到账" % (
            str(round(user_info["remain"], 2))
        )
        content = content + "亲，可以发送“查询”两个字，查询账户"
    else:
        logging.info(openid + " 提现短信发送失败  " + jsData["Message"])
        content = "系统维护中，请联系管理员。"
    replyMsg = reply.TextMsg(toUser, fromUser, content)
    return replyMsg.send()
