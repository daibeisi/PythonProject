# -*- coding: utf-8 -*-
import requests
import json
import logging
import threading
import datetime

_logger = logging.getLogger(__name__)

# 创建控制台显示的处理器，并设置 error 级别
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# 将处理器添加到记录器上
_logger.addHandler(ch)


class QYMP:
    _instance = None
    _lock = threading.RLock()

    def __init__(self, corpid: str, corpsecret: str):
        self.corpid = corpid
        self.corpsecret	 = corpsecret
        self.access_token = ""
        self.access_token_expires_time = datetime.datetime.now()
        self.get_access_token()

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        with cls._lock:
            if not cls._instance:
                cls._instance = super(QYMP, self).__new__(cls)
            return cls._instance

    def get_access_token(self):
        """ 获取access_token及过期时间 """
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&" \
              "corpsecret={corpsecret}".format(corpid=self.corpid, corpsecret=self.corpsecret)
        try:
            res = requests.get(url=url)
        except Exception as exc:
            _logger.error("{0}  {1}".format(exc, "微信auth.getAccessToken接口网络连接错误"))
        else:
            res_json = res.json()
            errcode = res_json.get("errcode")
            if errcode == 0:
                self.access_token = res_json.get('access_token')
                expires_in = res_json.get("expires_in")
                self.access_token_expires_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            else:
                errmsg = res_json.get("errmsg")
                _logger.error(str(errcode) + "微信auth.getAccessToken接口获取access_token失败" + errmsg)

    def ensure_access_token_effective(self):
        """ 确保access_token有效 """
        now_datetime = datetime.datetime.now()
        if not self.access_token or now_datetime >= self.access_token_expires_time:
            self.get_access_token()

    def get_user_id(self, js_code):
        """ 获取用户 userid """
        self.ensure_access_token_effective()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/miniprogram/jscode2session?' \
              'access_token={access_token}&js_code={js_code}&' \
              'grant_type=authorization_code'.format(access_token=self.access_token, js_code=js_code)
        try:
            res = requests.get(url=url)
        except Exception as exc:
            _logger.error("{0}  {1}".format(exc, "微信code2Session接口网络连接错误"))
        else:
            res_json = res.json()
            errcode = res_json.get("errcode", 0)
            if errcode == 0:
                userid = res_json.get("userid")
                return userid
            else:
                errmsg = res_json.get("errmsg")
                _logger.error(str(errcode) + "微信auth.code2Session接口获取userid失败" + errmsg)

    def get_department_list(self, dep_id=None):
        """ 获取部门列表 """
        self.ensure_access_token_effective()
        url = "https://qyapi.weixin.qq.com/cgi-bin/department/list?" \
              "access_token={access_token}".format(access_token=self.access_token)
        if dep_id is not None:
            url += "&id={dep_id}".format(dep_id=dep_id)
        try:
            res = requests.get(url=url)
        except Exception as exc:
            _logger.error("{0}  {1}".format(exc, "获取部门列表接口网络连接错误"))
        else:
            res_json = res.json()
            errcode = res_json.get("errcode")
            if errcode == 0:
                department_list = res_json.get('department')
                return department_list
            else:
                errmsg = res_json.get("errmsg")
                _logger.error(str(errcode) + "获取部门列表接口获取access_token失败" + errmsg)

    def get_department_user_info_list(self, dep_id):
        """ 获取成员ID列表 """
        self.ensure_access_token_effective()
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/list?" \
              "access_token={access_token}&department_id=" \
              "{dep_id}".format(access_token=self.access_token, dep_id=dep_id)
        try:
            res = requests.get(url=url)
        except Exception as exc:
            _logger.error("{0}  {1}".format(exc, "获取部门列表接口网络连接错误"))
        else:
            res_json = res.json()
            errcode = res_json.get("errcode")
            if errcode == 0:
                userlist = res_json.get("userlist")
                return userlist
            else:
                errmsg = res_json.get("errmsg")
                _logger.error(str(errcode) + "获取部门列表接口获取access_token失败" + errmsg)

    def send_text(self, content, touser=None, toparty=None):
        self.ensure_access_token_effective()
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?" \
                       "access_token=%s" % self.access_token
        data = {
            "touser": touser,
            "toparty": toparty,
            "msgtype": "text",
            "agentid": 1000004,
            "text": {
                "content": content
            }
        }
        try:
            res = requests.post(url, data=json.dumps(data))
        except Exception as exc:
            _logger.error("{0}  {1}".format(exc, "发送企业微信应用消息接口网络连接错误"))
        else:
            res_json = res.json()
            errcode = res_json.get("errcode")
            if errcode == 0:
                return True
            else:
                errmsg = res_json.get("errmsg")
                _logger.error(str(errcode) + "发送企业微信应用消息失败" + errmsg)


if __name__ == '__main__':
    qymp = QYMP(corpid="", corpsecret="")
    qymp.send_text('测试11111', '')
    department_list = qymp.get_department_list()
    print(department_list)
    for department in department_list:
        department_user_info_list = qymp.get_department_user_info_list(department['id'])
        print(department_user_info_list)
