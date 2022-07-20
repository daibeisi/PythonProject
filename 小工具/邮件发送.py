# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText


class SendEmail:
    """发送邮件模块"""
    def __init__(self, host, user, password):
        """初始化邮件配置服务"""
        self._mail_host = host  # smtp服务器
        self._send_user = user  # 需要登录的邮箱账号
        self._password = password  # 邮箱密码或者授权码,需要开启smtp

    def send_mail(self, to_addrs, subject, content):
        """执行发送邮件"""
        from_addr = "发件人名称" + "<" + self._send_user + ">"
        msg = MIMEText(content, "plain", "utf8")
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ";".join(to_addrs) if isinstance(to_addrs, list) else to_addrs
        try:
            server = smtplib.SMTP_SSL(self._mail_host, 465)  # 启用SSL发信, 端口一般是465
            server.login(self._send_user, self._password)  # 登录验证
            server.sendmail(from_addr, to_addrs, msg.as_string())  # 发送
            server.quit()
        except Exception as e:
            raise RuntimeError("发送失败".center(60, '='))


if __name__ == '__main__':
    sm = SendEmail(host='smtp.163.com', user='*', password='*')
    sm.send_mail("1935039743@qq.com", "测试通知", "宁好啊")