# -*- coding: utf-8 -*-
import top.api

appkey = "********"  # 这里填写淘宝联盟开发者平台的appkey
secret = "********************"  # 对应的secret


def orders(start_time, query_type="create_time", order_scene=1, span=1200):
    req = top.api.TbkOrderGetRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    req.fields = "tb_trade_parent_id,tb_trade_id,num_iid,item_title,item_num,price,pay_price,seller_nick,seller_shop_title,commission,commission_rate,unid,create_time,earning_time,tk3rd_pub_id,tk3rd_site_id,tk3rd_adzone_id,relation_id,tb_trade_parent_id,tb_trade_id,num_iid,item_title,item_num,price,pay_price,seller_nick,seller_shop_title,commission,commission_rate,unid,create_time,earning_time,tk_status,tk3rd_pub_id,tk3rd_site_id,tk3rd_adzone_id,special_id,click_time"
    req.start_time = start_time
    req.span = span
    req.page_no = 1
    req.page_size = 20
    req.tk_status = 1
    req.order_query_type = query_type
    req.order_scene = order_scene
    req.order_count_type = 1
    try:
        resp = req.getResponse()
    except top.api.base.TopException:
        return None
    return resp['tbk_order_get_response']['results']['n_tbk_order']


def newOrders(start_time, end_time, query_type=2, page_size=20, order_scene=2, member_type=2, page_no=1):
    req = top.api.TbkOrderDetailsGetRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    req.query_type = query_type
    req.page_size = page_size
    req.member_type = member_type
    req.end_time = end_time
    req.start_time = start_time
    req.page_no = page_no
    req.order_scene = order_scene
    try:
        resp = req.getResponse()  # 双十一/十二如果是订单超过30分钟，会提示错误。
    except top.api.base.TopException:
        return None  # 系统繁忙错误
    try:
        return resp['tbk_order_details_get_response']['data']['results']['publisher_order_dto']
    except KeyError:
        return resp['tbk_order_details_get_response']['data']['results']


def tpwd_create(text, url):
    req = top.api.TbkTpwdCreateRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    req.user_id = "32003052"
    req.text = text  # 口令弹框内容 一般填写商品标题
    req.url = url  # 口令跳转目标页
    req.logo = "https://app.budeniao.net/logo.jpg"  # 口令弹框logoURL
    resp = req.getResponse()
    return resp['tbk_tpwd_create_response']['data']['model']


def item_convert(num_iids, adzone_id=101473650037):
    req = top.api.TbkItemConvertRequest()
    req.set_app_info(top.appinfo(appkey, secret))
    req.fields = "num_iid,click_url"
    req.num_iids = num_iids  # 商品id
    req.adzone_id = adzone_id  # 推广位最后一位
    req.platform = 1
    req.unid = "demo"
    req.dx = "1"
    resp = req.getResponse()
    return resp['tbk_item_convert_response']['results']['n_tbk_item'][0]
