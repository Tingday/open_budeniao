# coding=utf-8
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


#  关于这个文件的说明，这个文件我已经做了防隐私泄落处理，这个是通过阿里云接口进行短信通知的，需要开发者进行配置。
#  如果有疑问可以联系我 woyufan@163.com


# 管理员接收 提现信息
def smsTiXian(openid, money, account, name):
    client = AcsClient('************', '************', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('PhoneNumbers', '*********')
    request.add_query_param('SignName', '***')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam',
                            '{"openid":"%s", "money":%s, "account":"%s", "name":"%s"}' % (openid, money, account, name))

    response = client.do_action_with_exception(request)
    return response


# 管理员 数据库信息
def smssql(reason):
    client = AcsClient('*********', '*********', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', '*********')
    request.add_query_param('SignName', '*********')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam', '{"reason":"%s"}' % (reason))

    response = client.do_action_with_exception(request)
    return response


#  手机注册验证码
def sms_via_code(code, phonenumber):
    client = AcsClient('*********', '*********', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', phonenumber)
    request.add_query_param('SignName', '*********')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam', '{"code":"%s"}' % (code))

    response = client.do_action_with_exception(request)
    return response


# 动态登录验证码
def sms_user_via_code(code, phonenumber):
    client = AcsClient('*********', '*********', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('PhoneNumbers', phonenumber)
    request.add_query_param('SignName', '*********')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam', '{"code":"%s"}' % (code))
    response = client.do_action_with_exception(request)
    return response


#  系统故障
def sms_system_error(reason):
    client = AcsClient('*********', '*********', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', '*********')
    request.add_query_param('SignName', '*********')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam', '{"reason":"%s"}' % (reason))

    response = client.do_action_with_exception(request)
    return response


#  通用消息通知
def sms_system_info(message):
    client = AcsClient('*********', '*********', 'default')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', '*********')
    request.add_query_param('SignName', '*********')
    request.add_query_param('TemplateCode', '*********')
    request.add_query_param('TemplateParam', '{"message":"%s"}' % (message))

    response = client.do_action_with_exception(request)
    return response


if __name__ == "__main__":
    res = sms_user_via_code("*********", "*********")
    print(res)
