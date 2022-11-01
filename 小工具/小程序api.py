# -*- coding: utf-8 -*-
import json
import requests
import logging
import threading

_logger = logging.getLogger(__name__)

# 创建控制台显示的处理器，并设置 error 级别
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# 将处理器添加到记录器上
_logger.addHandler(ch)


class MiniProgram(object):
    _instance = None
    _lock = threading.RLock()

    def __init__(self, appid: str, secret: str, redis=tt_redis):
        """ 初始化

        :param appid:
        :param secret:
        :param redis:
        """
        self.appid = appid  # 小程序appid
        self.secret = secret  # 小程序secret
        self.redis = redis  # redis

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = super(MiniProgram, cls).__new__(cls, *args, **kwargs)
            return cls._instance

    def get_user_id_info(self, js_code, num_tries=3):
        """获取用户openid、session_key、unionid

        :param str js_code: 通过 wx.login 接口获得临时登录凭证 code
        :param int num_tries: 重试次数,默认3次
        :return: id_info = {openid、session_key、unionid（绑定开放平台才有）}
        """
        user_id_info = json.loads(self.redis.str_get(js_code)) if self.redis.str_get(js_code) else {}
        if not user_id_info:
            url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&' \
                  'grant_type=authorization_code'.format(appid=self.appid, secret=self.secret, js_code=js_code)
            try:
                res = requests.get(url=url)
            except Exception as exc:
                _logger.error("{0}  {1}".format(exc, "微信auth.code2Session接口网络连接错误"))
            else:
                res_json = res.json()
                errcode = res_json.get("errcode", 0)
                if errcode == 0:
                    user_id_info = res_json
                    self.redis.str_set(js_code, json.dumps(user_id_info), 600)
                elif errcode == -1 and num_tries > 1:
                    return self.get_user_id_info(js_code, num_tries - 1)
                else:
                    _logger.error(str(errcode) + "微信auth.code2Session接口获取openid、session_key、unionid失败")
        return user_id_info

    def get_access_token(self, num_tries=3):
        """获取小程序全局唯一后台接口调用凭据

        通过微信 auth.getAccessToken 接口获取小程序全局唯一后台接口调用凭据（access_token）存入redis（过期时间为
        auth.getAccessToken返回参数为 expires_in）。
        access_token 的有效期目前为 2 个小时，需定时刷新，重复获取将导致上次获取的 access_token 失效。

        :param num_tries: 重试次数,默认3次
        :return: access_token
        """
        access_token = self.redis.str_get("access_token")
        if not access_token:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret=" \
                  "{secret}".format(appid=self.appid, secret=self.secret)
            try:
                res = requests.get(url=url)
            except Exception as exc:
                _logger.error("{0}  {1}".format(exc, "微信auth.getAccessToken接口网络连接错误"))
            else:
                res_json = res.json()
                errcode = res_json.get("errcode", 0)
                if errcode == 0:
                    access_token = res_json.get("access_token")
                    expires_in = res_json.get("expires_in", 7200) - 200
                    self.redis.str_set("access_token", access_token, expires_in)
                elif errcode == -1 and num_tries > 1:
                    return self.get_access_token(num_tries - 1)
                else:
                    _logger.error(str(errcode) + "微信auth.getAccessToken接口获取access_token失败")
        return access_token

    def get_phone_number(self, code, num_tries=3):
        """获取用户微信绑定的手机号（国外手机号会有区号）

        code换取用户手机号。 每个code只能使用一次，code的有效期为5min，与 wx.login 返回的 code 作用是不一样的，不能混用。

        :param code: getPhoneNumber 返回的 code 与 wx.login 返回的 code 作用是不一样的，不能混用。
        :param num_tries: 重试次数,默认3次
        :return: phone_number
        """
        phone_number = self.redis.str_get(code)
        if not phone_number:
            access_token = self.get_access_token()
            if access_token :
                url = "https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={0}".format(access_token)
                headers = {'Content-Type': 'application/json', "Accept": "application/json"}
                data = {"code": code}
                try:
                    res = requests.post(url=url, data=json.dumps(data), headers=headers)
                except Exception as exc:
                    _logger.error("{0}  {1}".format(exc, "微信phonenumber.getPhoneNumber接口网络连接错误"))
                else:
                    res_json = res.json()
                    errcode = res_json.get("errcode", 0)
                    if errcode == 0:
                        phone_info = res_json.get("phone_info")
                        if phone_info:
                            phone_number = phone_info.get("phoneNumber")
                            self.redis.str_set(code, phone_number, 600)
                    elif errcode == -1 and num_tries > 1:
                        return self.get_phone_number(code, num_tries - 1)
                    else:
                        _logger.error(str(errcode) + "微信phonenumber.getPhoneNumber接口获取phone_number失败")
            else:
                _logger.error("微信phonenumber.getPhoneNumber接口获取phone_number,缺少必要参数")
        return phone_number


wechatApi = MiniProgram(appid="", secret="")

# Only export 'wechatApi'
__all__ = ['wechatApi']

if __name__ == '__main__':
    phone_number = wechatApi.get_phone_number(code="")
