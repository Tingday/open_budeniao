# -*- coding:utf8 -*-
import linksql
import time
import alimama
import logging

logger = logging.getLogger()

def truetime(order_scene=1):#实时20分钟订单
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 1200))
    tk_orders = getTwentyOrders(start_time, order_scene)
    if tk_orders:linksql.OrderDetailsAdd(tk_orders)

def twenty(start_time,order_scene):
    tk_orders = getTwentyOrders(startTime=start_time,order_scene = order_scene)
    if tk_orders:linksql.OrderDetailsAdd(tk_orders)

def getTwentyOrders(start_time,order_scene=2):#阿里巴巴淘宝联盟拉取订单的新代码alibaba.newOrders
    struct_time = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    mktime = time.mktime(struct_time) + 1200 #获得20分钟后的时间
    end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(mktime))#转化为时间字符串
    webdata = alimama.newOrders(start_time,end_time,order_scene=order_scene)
    return webdata

def getThreeHoursOrders(start_time,order_scene=1):#获得指定日期的订单
    struct_time = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    mktime = time.mktime(struct_time) + 10800 #获得3小时后的时间
    end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(mktime))#转化为时间字符串
    # print(start_time, end_time)
    tk_orders = alimama.newOrders(start_time,end_time,order_scene=order_scene)
    return tk_orders

def todayorders(date, order_scene=1): 
    # 一天的订单收录； 正常来说使用updateTodayOrders即可；
    # 如果是双十一/双十二 节日，那么使用本接口来正常收录，速度可能比较慢。
    time_list = ["00:00:00", "00:20:00", "00:40:00",
                 "01:00:00", "01:20:00", "01:40:00",
                 "02:00:00", "02:20:00", "02:40:00",
                 "03:00:00", "03:20:00", "03:40:00",
                 "04:00:00", "04:20:00", "04:40:00",
                 "05:00:00", "05:20:00", "05:40:00",
                 "06:00:00", "06:20:00", "06:40:00",
                 "07:00:00", "07:20:00", "07:40:00",
                 "08:00:00", "08:20:00", "08:40:00",
                 "09:00:00", "09:20:00", "09:40:00",
                 "10:00:00", "10:20:00", "10:40:00",
                 "11:00:00", "11:20:00", "11:40:00",
                 "12:00:00", "12:20:00", "12:40:00",
                 "13:00:00", "13:20:00", "13:40:00",
                 "14:00:00", "14:20:00", "14:40:00",
                 "15:00:00", "15:20:00", "15:40:00",
                 "16:00:00", "16:20:00", "16:40:00",
                 "17:00:00", "17:20:00", "17:40:00",
                 "18:00:00", "18:20:00", "18:40:00",
                 "19:00:00", "19:20:00", "19:40:00",
                 "20:00:00", "20:20:00", "20:40:00",
                 "21:00:00", "21:20:00", "21:40:00",
                 "22:00:00", "22:20:00", "22:40:00",
                 "23:00:00", "23:20:00", "23:40:00"]
    for timetext in time_list:
        start_time = date + " " + timetext
        print(start_time, "收录开始")
        time.sleep(0.3)
        tk_orders = getTwentyOrders(start_time, order_scene)
        if tk_orders:
            for tk_order in tk_orders:
                logging.info(tk_order['item_title'])
            linksql.OrderDetailsAdd(tk_orders)
    return None
        

def updateTodayOrders(date,order_scene=1):#date格式%Y-%m-%d 将返回进度
    ''' 
    非双节日常订单收录 
    '''
    start_time_list = ["00:00:00","03:00:00","06:00:00","09:00:00","12:00:00","15:00:00","18:00:00","21:00:00"] 
    logging.info("下面进行%s日期的订单收录"%(date))
    for timetext in start_time_list:
        start_time = date + " " + timetext
        tk_orders = getThreeHoursOrders(start_time) #获得列表
        if tk_orders:
            tk_orders_nu = len(tk_orders)
            if tk_orders_nu > 0:
                logging.info(timetext + "共有%s个订单分别如下："%(tk_orders_nu))
            time.sleep(1)
            for tk_order in tk_orders:
                logging.info(tk_order['item_title'])
            linksql.OrderDetailsAdd(tk_orders)
    return None

def trueTimeTxt():#返回昨天的日期
    timetxt = time.strftime("%Y-%m-%d",time.localtime(time.time() - 86400))#获得昨天的日期
    return timetxt

def trueTimeDate():#返回今天的日期零点时间
    timetxt = time.strftime("%Y-%m-%d", time.localtime(time.time())) + ' 00:00:00'
    return timetxt

def reinclude():
    timetxt = trueTimeTxt()#昨天的日期%Y-%m-%d
    lstimetxt = lastIncludeTime()#上一次的执行时间%Y-%m-%d %H:%M:%S
    timeDateTxt = trueTimeDate()#今天的日期零点时间
    if(timetxt in lstimetxt):#表示正在运行
        struct_time = time.strptime(lstimetxt,'%Y-%m-%d %H:%M:%S') #获得时间元组
        secs = time.mktime(struct_time) + 240#获得上次时间元组的时间戳，并计算得出目前的时间戳（加120s）
        thistimetxt = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(secs))#
        getTwentyOrders(thistimetxt,1)
    else:
        thistimetxt = timetxt + ' 00:00:00'
        getTwentyOrders(thistimetxt,1)
    writeIncludeTime(thistimetxt)
    return thistimetxt

def ReIncludeFromArray(array_time, stay):#从一组时间中重新收录
    for timestp in array_time:
        if timestp and len(timestp) == 19:
            getTwentyOrders(timestp,1)
        print(timestp + " 已收录")
        time.sleep(stay)#推迟执行
    return None
            
def lastIncludeTime():#
    f = open('includetime.txt','r')
    timetxt = f.read()
    f.close()
    return timetxt

def writeIncludeTime(timetxt):
    f = open('includetime.txt','w')
    f.write(timetxt)
    f.close()
    return timetxt
    
def updateOrders():
    orders = linksql.month_order()
    if orders:
        logger.info('本月一共有%s个订单'%(str(len(orders))))
        for order in orders:
            tk_status = order["tk_status"]; #订单状态
            tk_create_time = order["create_time"];#订单创建时间
            tk_orders_rid = getTwentyOrders(tk_create_time)
            tk_orders_pid = getTwentyOrders(tk_create_time, 1)
            if tk_orders_rid:
                for tk_order in tk_orders_rid:
                    linksql.updateorder(tk_order)
            elif tk_orders_pid:
                for tk_order in tk_orders_pid:
                    linksql.updateorder(tk_order)
            else:
                print(order)
                logger.warning('月订单更新出错 rid/pid 未找到.')
            time.sleep(1)#延迟40秒
    else:
        logger.warning('本月没有订单')

