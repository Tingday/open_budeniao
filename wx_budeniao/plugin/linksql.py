# -*-coding:utf8 -*-
# filename:linksql.py
# print(sys.path)
import sqlite3
import time
import sms
import weixin
import logging
import dbtool

logger = logging.getLogger()  # 全局的logger


def alipay(phone, name, openid):  # 支付宝账号绑定,此处要防止sql注入
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    res_sql = user_info_by_openid(openid)
    if res_sql:
        user_info = res_sql[0]  # 获取用户信息
        user_alipay = user_info["alipay"]
        if user_alipay is None:
            args = (phone, name, openid)
            db_res = curs.execute('UPDATE user SET alipay=?, xingming=? WHERE openid =?;', args)
            conn.commit()
            conn.close()
            return db_res
        else:
            conn.close()
            return None
    else:
        conn.close()
        return None


def setProxy(openid, proxy, force=False):  # 设置代理
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT proxy FROM user WHERE openid=?;', args)
    sqldata = curs.fetchone()
    if sqldata[0] and force is False:
        conn.close()
        return False
    else:
        args = (proxy, openid,)
        curs.execute('UPDATE user SET proxy=? WHERE openid=?;', args)
        conn.commit()
        conn.close()
        return True


def checkalipay(openid):  # 是否可以提现
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT * FROM user WHERE openid=? AND alipay IS NOT NULL;', args)
    sqldata = curs.fetchone()
    if sqldata:
        conn.close()
        return True
    else:
        conn.close()
        return False


def publisher(openid):  # 检查是否已备案渠道 有备案则返回渠道关系id
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT relation_id FROM beian WHERE openid =?;', args)
    sqldata = curs.fetchone()
    if sqldata:
        return sqldata[0]


def openidpid(openid):  # 从pid关系库获得pid，用于优惠券查询等
    # 这里增加优先查找openidrid关系，如果有直接返回None
    rid = openidrid(openid)
    if rid:
        print("用户存在rid关系，已备案。")
        return None
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT adzone_id FROM pid WHERE openid =?;', args)
    sqldata = curs.fetchone()
    if sqldata:
        return sqldata[0]


def checktixian(openid):  # 提现资格申请
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT * FROM user WHERE openid=? AND rgoods > qiandao;', args)
    sqldata = curs.fetchall()
    return sqldata


def tixian(openid):  # 提现申请
    user_info_x = user_info_by_openid(openid)
    if user_info_x:
        user_info = user_info_x[0]
    else:
        return None
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (user_info["remain"], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            float(user_info["remain"]) + float(user_info["cashed"]), openid)
    curs.execute('UPDATE user SET cash=?, remain=0, cashed_time=?, cashed=? WHERE openid=?;', args)
    db_res = curs.fetchall()
    conn.commit()
    conn.close()
    return db_res


def rm_user(openid):  # 删除openid下的用户信息
    if user_info_by_openid(openid) is None:
        pass
        return None
    db = dbtool.simpleToolSql()
    sql = "DELETE FROM user WHERE openid =?;"
    args = (openid,)
    db_res = db.execute(sql, args)
    db.close()
    return db_res


# 获得提现中的列表
def cash_now():
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM user WHERE cash > 0;"
    args = ()
    db_res = db.query(sql, args)
    db.close()
    return db_res


def isnewuser(openid):  # 判断用户是否存在
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    query = "SELECT * FROM user WHERE openid='%s';" % openid
    curs.execute(query)
    sqldata = curs.fetchone()
    conn.close()
    if sqldata:
        return False
    else:
        return True


def create_new_user(openid):  # 创建一个新用户
    db = dbtool.simpleToolSql()
    sql = "INSERT INTO user (openid, level, cashed, remain, disabled, orders, num, cash, goods, qiandao, level_coefficient,rgoods,gift, proxy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, ?);"
    params = (openid, 'youhuihuodong', 0, 0, 0, 0, 0, 0, 0, 0, 0.9, 0, 0, "o1mDH1HT8Nf7EdDc2-WJbw8mXkvk")
    sql_res = db.execute(sql, params)
    db.close()
    # sms.smssql("新用户")
    return sql_res


def qiandao(openid, qian):  # 签到金额加入数据库
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    query = "UPDATE user SET qiandao=qiandao + %f WHERE openid= %s;" % (qian, openid)
    curs.execute(query)
    query = 'UPDATE user SET lastdate=%s WHERE openid=%s;' % (time.strftime('%Y-%m-%d', time.localtime()), openid)
    curs.execute(query)
    conn.commit()
    conn.close()
    return None


def month_order():  # 本月结算前的所有订单
    conn = sqlite3.connect('taobaokesql.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    localtime = time.localtime(time.time())
    tmday = localtime[2]
    if int(tmday) >= 21:  # 21号月结
        sql = "SELECT * FROM orders WHERE create_time like ?;"
        params = (time.strftime("%Y-%m%", time.localtime()),)
    else:
        sql = "SELECT * FROM orders WHERE create_time like ? OR create_time like ?;"
        params = (
            time.strftime("%Y-%m%", time.localtime(time.time() - 2592000)), time.strftime("%Y-%m%", time.localtime()))
    curs.execute(sql, params)
    orders = curs.fetchall()
    return orders


def updateorder(order):  # 更新订单入库
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    if "tk_earning_time" in order:
        query = 'UPDATE orders SET pay_price=%f, commission=%f, earning_time=%s, tk_status=%s, click_time=%s WHERE trade_id = %s;' % (
            float(order['pay_price']), float(order['pub_share_fee']), order['tk_earning_time'], order['tk_status'],
            order['tk_create_time'], order['trade_id'])
    else:
        query = 'UPDATE orders SET commission=%f, tk_status=%s, click_time=%s WHERE trade_id = %s;' % (
            float(order['pub_share_fee']), order['tk_status'], order['tk_create_time'], order['trade_id'])
    curs.execute(query)
    conn.commit()
    conn.close()
    logger.info('订单更新 ' + str(order['trade_id']) + ' ' + order['tk_create_time'])
    return str(order['trade_id'])  # 成功则返回订单号


def cash(openid):  # 完成用户提现
    if not (iscashing(openid)):
        return {'error': 1, 'msg': '用户未申请提现'}
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    args = (timestr, openid)
    curs.execute('UPDATE user SET cash=0, cashed_time=? WHERE openid =?;', args)
    conn.commit()
    conn.close()
    if iscashing(openid):
        return {'error': 2, 'msg': '提现出错，请检查函数'}
    else:
        logger.info(openid + ' 提现成功')
        return {'error': 0, 'msg': '提现成功'}


def completed_tixian(xingming, openid):  # 提现
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    query = 'SELECT openid FROM user WHERE openid LIKE %s;' % ('%' + openid)
    curs.execute(query)
    sqldata = curs.fetchone()
    newopenid = sqldata[0]
    query = 'UPDATE user SET cash=0, cashed_time=%s WHERE xingming=%s AND openid = %s;' % (
        timestr, xingming, newopenid)
    curs.execute(query)
    query = 'SELECT cashed_time FROM user WHERE openid = %s;' % newopenid
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata[0]:  # openid存在
        if sqldata[0] == timestr:  # 修改成功
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    else:
        conn.close()
        return False


# 更新代理中获得的金额proxy_money
def updateProxyMoney(openid):
    proxy_coefficient = 0.25  # 代理系数
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    conn.row_factory = dict_factory
    args = (proxy_coefficient, openid,)
    curs.execute("SELECT SUM(cashed) * ? FROM user WHERE proxy=?;", args)
    sqldata = curs.fetchone()
    if sqldata:
        # 保存
        if sqldata[0]:
            proxy_money = sqldata[0]
        else:
            proxy_money = 0
        args = (proxy_money, openid,)
        curs.execute("UPDATE user SET proxy_money = ? WHERE openid = ?;", args)
        conn.commit()
    conn.close()
    return sqldata


# 更新代理数
def updateProxyNum(openid):
    conn = sqlite3.connect("taobaokesql.db")
    curs = conn.cursor()
    conn.row_factory = dict_factory
    args = (openid,)
    curs.execute("SELECT COUNT(*) FROM user WHERE proxy=?", args)
    sqldata = curs.fetchone()
    if sqldata:
        # 保存
        proxyNum = sqldata[0]
        args = (proxyNum, openid,)
        curs.execute("UPDATE user SET num = ? WHERE openid = ?", args)
        conn.commit()
    conn.close()
    return sqldata


# 更新用户的remain orders
def updateUser(openid):  # 更新用户的remain orders
    user_info_x = user_info_by_openid(openid)
    if user_info_x:
        user_info = user_info_x[0]
    else:
        return None
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    # 用户信息更新
    # proxy
    args_openid_only = (openid,)
    query = 'SELECT COUNT(*) FROM user WHERE proxy=?;'
    curs.execute(query, args_openid_only)
    sqldata = curs.fetchone()
    if sqldata[0]:
        num = int(sqldata[0])
    else:
        num = 0
    args = (num, openid)
    query = 'UPDATE user SET num =? WHERE openid = ?;'
    curs.execute(query, args)

    # 订单
    query = 'SELECT count(*) FROM ORDERS WHERE  (tk_status=12 or tk_status=3 or tk_status=14) AND openid=?;'
    curs.execute(query, args_openid_only)
    sqldata = curs.fetchone()
    if sqldata[0]:
        money_orders = int(sqldata[0])
        query = 'UPDATE user SET orders=%d WHERE openid=%s;' % (money_orders, openid)
        curs.execute(query)
    else:
        query = 'UPDATE user SET orders=0 WHERE openid=%s;' % openid
        curs.execute(query)
    query = 'SELECT sum(pub_share_pre_fee) FROM orders WHERE (tk_status=3 or tk_status=14) and openid=%s;' % (
        openid)  # 3订单结算 14 订单成功 总可用收入
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata[0]:
        money_enabled = float(sqldata[0])
        money_rgoods = money_enabled * float(user_info["level_coefficient"])
        query = 'UPDATE user SET rgoods=%f WHERE openid=%s;' % (money_rgoods, openid)
        curs.execute(query)
        money_remain = money_rgoods - float(user_info["cashed"]) + float(user_info["qiandao"]) + float(
            user_info["gift"])  # 可用收入= 总收入 - 已提现收入
        query = 'UPDATE user SET remain=%f WHERE openid=%s;' % (money_remain, openid)
        curs.execute(query)
    else:
        money_remain = float(user_info["qiandao"]) + float(user_info["gift"]) - float(user_info["cashed"])
        query = 'UPDATE user SET remain=%f WHERE openid=%s;' % (money_remain, openid)
        curs.execute(query)
    query = 'SELECT sum(pub_share_pre_fee) FROM orders WHERE tk_status=12 and openid=%s;' % openid  # 12 订单付款 未收货收入
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata[0]:
        money_goods = float(sqldata[0]) * user_info["level_coefficient"]
        query = 'UPDATE user SET goods=%f WHERE openid=%s;' % (money_goods, openid)
        curs.execute(query)
    else:
        query = 'UPDATE user SET goods=0 WHERE openid=%s;' % openid
        curs.execute(query)
    query = 'SELECT sum(pub_share_pre_fee) FROM orders WHERE tk_status=13 and openid=%s;' % openid  # 13 订单失效 失败订单收入
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata[0]:
        money_disabled = float(sqldata[0]) * user_info["level_coefficient"]
        query = 'UPDATE user SET disabled=%f WHERE openid=%s;' % (money_disabled, openid)
        curs.execute(query)
    else:
        query = 'UPDATE user SET disabled=0 WHERE openid=%s;' % openid
        curs.execute(query)
    conn.commit()
    conn.close()
    # 更新代理金额
    updateProxyMoney(openid)
    updateProxyNum(openid)
    return openid + " update!"


def pidopenid(adzone_id):  # pid模式 从pid获取openid
    conn = sqlite3.connect('taobaokesql.db')
    conn.row_factory = dict_factory  # 使数据库直接返回字典
    curs = conn.cursor()
    params = (adzone_id,)
    query = "SELECT * FROM pid WHERE adzone_id=?;"
    curs.execute(query, params)
    sqldata = curs.fetchall()
    conn.commit()
    conn.close()
    return sqldata


def removepid(openid):  # 限已有rid 的情况，可以删除pid，为下一步全面接入rid作准备
    if not (openidrid(openid)):
        return None
    if not (openidpid(openid)):
        return None
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('DELETE FROM pid WHERE openid=?;', args)
    conn.commit()
    conn.close()
    return True


def openidrid(openid):  # 从openid获得rid用来拼接优惠券。
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT relation_id FROM beian WHERE openid =?;', args)
    sqldata = curs.fetchone()
    conn.close()
    if sqldata:
        return sqldata[0]


def ridopenid(relation_id):  # rid模式 从relation_id 获取 openid
    conn = sqlite3.connect('taobaokesql.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    args = (relation_id,)
    curs.execute('SELECT openid FROM beian WHERE relation_id =?;', args)
    sqldata = curs.fetchall()
    return sqldata


def getuserid(openid):
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    query = 'SELECT userid FROM user WHERE openid =%s;' % openid
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata[0]:
        userid = sqldata[0]
        conn.commit()
        conn.close()
        return userid
    else:
        conn.close()
        return None


def iscashing(openid):
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT * FROM user WHERE cash > 0 AND openid=?;', args)
    sqldata = curs.fetchone()
    conn.close()
    if sqldata:
        return True
    else:
        return False


def dict_factory(cursor, row):  # 这个是slqite3官方的把select结果以字典输出的方法函数；表示看不懂。
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def app_userinfo(openid):  # 查询用户信息app
    updateUser(openid)
    conn = sqlite3.connect('taobaokesql.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    args = (openid,)
    curs.execute('SELECT * FROM user WHERE openid =?;', args)
    sqldata = curs.fetchone()
    conn.close()
    return sqldata


def new_orders():
    conn = sqlite3.connect("taobaokesql.db")
    conn.row_factory = dict_factory
    curs = conn.cursor()
    sql = "SELECT * FROM orders ORDER BY click_time DESC LIMIT 25;"
    curs.execute(sql)
    db_res = curs.fetchall()
    conn.close()
    return db_res


def cashing():
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    query = 'SELECT * FROM user WHERE cash > 0;'
    curs.execute(query)
    sqldata = curs.fetchall()
    textdata = []
    if sqldata:
        for user in sqldata:
            if user[17]:
                text = {"openid": user[0], "xingming": user[17]}
                textdata.append(text)
    conn.close()
    return textdata


# pid使用状态，方便管理
def pid_status():
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM pid ORDER BY create_time desc limit 0,1;"  # 最新的pid
    res_pid = db.query(sql)
    sql_count = "SELECT COUNT(*) FROM pid;"  # 计算pid总数
    res_count = db.query(sql_count)
    db.close()
    res_pid_status = {"total": res_count, "last_pid": res_pid}
    return res_pid_status


# 建立新的绑定关系
def new_pid(openid):
    pid = openidpid(openid)
    rid = openidrid(openid)
    if pid or rid:
        logger.warning(openid + " pid关系已存在!")
        return None
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM pid ORDER BY create_time desc limit 0,1;"
    db_res = db.query(sql)
    print("pid获取最新一条", db_res)
    if db_res:
        last_id = db_res[0]["sequence"]
        new_id = int(last_id) + 1
    else:
        new_id = 1
        print("pid关系库为空")
    args = (new_id,)
    sql_new = "SELECT * FROM pidku WHERE id=?;"
    res_new = db.query(sql_new, args)
    if res_new:
        new_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        total = 186
        remain = total - new_id
        use_rate_new = new_id / total
        if use_rate_new > 0.9:
            sms.smssql("use_rate超过0.9")
        sql = "INSERT INTO pid (adzone_id, adzone_name, site_id, site_name, openid, create_time, sequence, remain, total, use_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        args = (
            res_new[0]["adzone_id"], res_new[0]["adzone_name"], res_new[0]["site_id"], res_new[0]["site_name"], openid,
            new_create_time, new_id, remain, total, use_rate_new)
        res_db = db.execute(sql, args)
        print("pid关系保存状况 linksql", res_db)
        sql_two = 'SELECT * FROM pid ORDER BY create_time desc limit 0,1;'
    else:
        logger.warning('pidku已空，告急')
        sms.smssql('pidku已空，告急')
        sql_two = 'SELECT * FROM pid WHERE adzone_name =10001;'  # 使用本人pid进行购买
    res_pid = db.query(sql_two)
    db.close()
    logger.warning(openid + " 创建了pid！")
    return res_pid


def getpid(openid):
    pid = openidpid(openid)
    rid = openidrid(openid)
    if pid or rid:
        return "openid has exist."
    conn = sqlite3.connect('taobaokesql.db')
    conn.row_factory = dict_factory
    curs = conn.cursor()
    query = 'SELECT * FROM pid ORDER BY create_time desc limit 0,1;'  # 按时间降序，取最新一条
    curs.execute(query)
    sqldata = curs.fetchone()
    if not sqldata:  # pid表为空
        new_id = 1
        query = 'SELECT * FROM pidku WHERE id=1;'
        curs.execute(query)
    else:
        last_id = sqldata["sequence"]  # 最新索引
        use_rate = sqldata["use_rate"]  # pid使用率
        if use_rate >= 0.9:
            sms.smssql('pid已满200个')
        args = (int(last_id) + 1,)
        query = "SELECT * FROM pidku WHERE id=?;"
        curs.execute(query, args)
        sqldata = curs.fetchone()  # pidku表中取数据
        if sqldata:  # pidku未满
            # print(sqldata)
            new_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            new_id = last_id + 1
            total = 186
            remain = total - new_id
            use_rate = new_id / total
            sql = "INSERT INTO pid (adzone_id, adzone_name, site_id, site_name, openid, create_time, sequence, remain, total, use_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
            args = (sqldata["adzone_id"], sqldata["adzone_name"], sqldata["site_id"], sqldata["site_name"], openid,
                    new_create_time, new_id, remain, total, use_rate)
            curs.execute(sql, args)
            query = 'SELECT * FROM pid ORDER BY create_time desc limit 0,1'
        else:
            logger.warning('pidku已空，告急')
            sms.smssql('pidku已空，告急')
            query = 'SELECT * FROM pid WHERE adzone_name =10001'  # 使用本人pid进行购买
    curs.execute(query)
    sqldata = curs.fetchone()
    conn.commit()
    conn.close()
    logger.info(openid + " pid created!")
    return sqldata


# todo 解除部分pidrelation
def release_pid():
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM user WHERE orders='0' and remain='0';"
    db_res = db.query(sql)
    db.close()
    return db_res


# 删除所有pid绑定关系！:
def clean_pid():
    db_res = release_pid()
    print("任务数量", len(db_res))
    print("注意备份数据库！")
    for pid_object in db_res:
        del_res = del_pid(pid_object["openid"])
        print(del_res, pid_object["openid"])
    return "完成任务！请检查数据库情况。"


def isneworder(order):
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    trade_id = str(order['trade_id'])
    query = 'SELECT * FROM orders WHERE trade_id=%s;' % trade_id
    curs.execute(query)
    sqldata = curs.fetchone()
    if sqldata:
        conn.close()
        return False
    else:
        conn.close()
        return True


# todo 删除pid关系
def del_pid(openid):
    db = dbtool.simpleToolSql()
    sql = "DELETE FROM pid WHERE openid=?;"
    args = (openid,)
    db_res = db.execute(sql, args)
    db.close()
    return db_res


def getorder(openid, trade_id):
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM orders WHERE trade_id=? AND openid=?;"
    args = (trade_id, openid,)
    db_res = db.query(sql, args)
    db.close()
    return db_res


def getOrderPlus(trade_id):
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM orders WHERE trade_id=?;"
    args = (trade_id,)
    db_res = db.query(sql, args)
    db.close()
    return db_res


def user_info_by_openid(openid):
    db = dbtool.simpleToolSql()
    args = (openid,)
    sql = "SELECT * FROM user WHERE openid =?;"
    sql_res = db.query(sql, args)
    db.close()
    return sql_res


def order_details_add_super(order, openid):
    exist_order_info = getOrderPlus(order["trade_id"])
    if exist_order_info:
        pass
        return None
    user_info = user_info_by_openid(openid)
    conn = sqlite3.connect('taobaokesql.db')
    curs = conn.cursor()
    conn.row_factory = dict_factory  # 使数据库直接返回字典
    args = (
        order['site_id'], order['tk_create_time'], order['order_type'], order['click_time'], order['pub_share_rate'],
        order['seller_nick'], order['item_price'], order['alipay_total_price'], order['trade_id'], order['item_num'],
        order['adzone_id'], order['terminal_type'], order['item_title'], order['tk_status'], order['seller_shop_title'],
        order['item_id'], order['subsidy_rate'], order['trade_parent_id'], order['income_rate'],
        order['total_commission_rate'], order['pub_share_pre_fee'], order['item_category_name'], openid)
    sql = "INSERT INTO orders(site_id, create_time, order_type, click_time, commission_rate, seller_nick, price, alipay_total_price, trade_id, item_num, adzone_id, terminal_type, item_title, tk_status, seller_shop_title, num_iid, subsidy_rate, trade_parent_id, income_rate, total_commission_rate, pub_share_pre_fee, auction_category, openid) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    curs.execute(sql, args)
    db_res = curs.fetchall()
    conn.commit()
    conn.close()
    logger.info(openid + ' 订单成功' + ' trade_id:' + str(order['trade_id']))
    print(openid + ' 订单成功' + ' trade_id:' + str(order['trade_id']))
    weixin.orderSuccess(openid, order, user_info[0]["level_coefficient"])  # 尝试发送订单卡片
    return db_res


def user_type(openid):
    if isnewuser(openid):
        return None
    pid = openidpid(openid)
    rid = openidrid(openid)
    if pid and rid is None:
        return "pid_user"
    if rid:
        return "rid_user"


def OrderDetailsAdd(orders):
    for order in orders:
        if getOrderPlus(order["trade_id"]):
            pass
            # logger.info(order["trade_id"] + " 存在")
            # print(order["trade_id"],"存在")
            continue
        if order["adzone_id"] == 85967650050:
            logger.warning("85967650050 error")
            print("85967650050 error", order["tk_create_time"], order["trade_id"])
            logger.warning("85967650050 error!")
            continue
        if "relation_id" in order:  # 查找pid来绑定关系
            rid = ridopenid(order['relation_id'])
            if rid:
                openid = rid[0]["openid"]  #
                order_details_add_super(order, openid)
            else:
                # 没有绑定关系，尝试绑定关系

                logger.warning('订单失败rid:' + str(order['relation_id']) + ' trade_id:' + str(order['trade_id']))
        else:  # 依然使用pid模式
            pid = pidopenid(order['adzone_id'])
            if pid:
                openid = pid[0]["openid"]
                order_details_add_super(order, openid)
            else:  # openid 不存在 找不到订单的主人
                logger.warning('订单失败pid无法找到：' + str(order['adzone_id']) + ' trade_id:' + str(order['trade_id']))
    return "done"


def wx_user_info_save(wx_user):
    db = dbtool.simpleToolSql()
    sql = "INSERT INTO weixin_user (openid, province, city, subscribe_time, headimgurl, language, country, remark, qr_scene, sex, qr_scene_str, subscribe, nickname, groupid, subscribe_scene) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    params = (wx_user["openid"], wx_user["province"], wx_user["city"], wx_user["subscribe_time"], wx_user["headimgurl"],
              wx_user["language"], wx_user["country"], wx_user["remark"], wx_user["qr_scene"], wx_user["sex"],
              wx_user["qr_scene_str"], wx_user["subscribe"], wx_user["nickname"], wx_user["groupid"],
              wx_user["subscribe_scene"])
    db_res = db.execute(sql, params)
    db.close()
    return db_res


def wx_user_info(wx_user):
    db = dbtool.simpleToolSql()
    sql = "SELECT * FROM weixin_user WHERE openid = ?;"
    params = (wx_user["openid"],)
    db_res = db.query(sql, params)
    db.close()
    return db_res


def wx_user_unsubscribe(openid):
    db = dbtool.simpleToolSql()
    sql = "UPDATE weixin_user SET subscribe = 0 WHERE openid = ?;"
    params = (openid,)
    db_res = db.execute(sql, params)
    db.close()
    return db_res


def user_list_openid(page=1, max_num=100):
    db = dbtool.simpleToolSql()
    sql = "SELECT openid FROM user LIMIT ? OFFSET ?;"
    params = (max_num, (page - 1) * max_num,)
    db_res = db.query(sql, params)
    db.close()
    return db_res


# 所有用户
def user_list(page=1, max_num=100, xingming_only=True):
    db = dbtool.simpleToolSql()
    if xingming_only:
        sql = "SELECT * FROM user WHERE xingming IS NOT NULL ORDER BY orders DESC LIMIT ? OFFSET ?;"
    else:
        sql = "SELECT * FROM user ORDER BY orders DESC LIMIT ? OFFSET ?;"
    params = (max_num, (page - 1) * max_num,)
    db_res = db.query(sql, params)
    db.close()
    return db_res


if __name__ == "__main__":
    test_openid = "o1mDH1FEGyPHWxhmBcfzuh5FV5FY"
    # res = user_info_by_openid(test_openid)
    # res = release_pid()
    # res = pid_status()
    res = openidpid(test_openid)
    print(res)
    res2 = openidrid(test_openid)
    print(res2)
