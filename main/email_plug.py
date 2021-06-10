import smtplib, os
import random
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


class SendMail(object):
    def __init__(self, username, passwd, recv, title, content,
                 file=None, ssl=False,
                 email_host='smtp.qq.com', port=25, ssl_port=465):
        '''
        :param username: 用户名
        :param passwd: 密码
        :param recv: 收件人，多个要传list ['a@qq.com','b@qq.com]
        :param title: 邮件标题
        :param content: 邮件正文
        :param file: 附件路径，如果不在当前目录下，要写绝对路径，默认没有附件
        :param ssl: 是否安全链接，默认为普通  不使用ssl
        :param email_host: smtp服务器地址，默认为qq服务器
        :param port: 非安全链接端口，默认为25
        :param ssl_port: 安全链接端口，默认为465
        '''
        self.username = username  # 用户名
        self.passwd = passwd  # 密码
        self.recv = recv  # 收件人，多个要传list ['a@qq.com','b@qq.com]
        self.title = title  # 邮件标题
        self.content = content  # 邮件正文
        self.file = file  # 附件路径，如果不在当前目录下，要写绝对路径
        self.email_host = email_host  # smtp服务器地址
        self.port = port  # 普通端口
        self.ssl = ssl  # 是否安全链接
        self.ssl_port = ssl_port  # 安全链接端口

    def send_mail(self):  # 发邮件函数
        msg = MIMEMultipart()
        # 发送内容的对象
        if self.file:  # 处理附件的
            file_name = os.path.split(self.file)[-1]  # 只取文件名，不取路径
            try:
                f = open(self.file, 'rb').read()
            except Exception as e:
                raise Exception('附件打不开！！！！')
            else:
                att = MIMEText(f, "base64", "utf-8")
                att["Content-Type"] = 'application/octet-stream'
                # base64.b64encode(file_name.encode()).decode()
                new_file_name = '=?utf-8?b?' + base64.b64encode(file_name.encode()).decode() + '?='
                # 这里是处理文件名为中文名的，必须这么写
                att["Content-Disposition"] = 'attachment; filename="%s"' % (new_file_name)
                msg.attach(att)
        msg.attach(MIMEText(self.content))  # 邮件正文的内容
        msg['Subject'] = self.title  # 邮件主题
        msg['From'] = self.username  # 发送者账号
        msg['To'] = ','.join(self.recv)  # 接收者账号列表

        if self.ssl:
            self.smtp = smtplib.SMTP_SSL(self.email_host, port=self.ssl_port)
        else:
            self.smtp = smtplib.SMTP(self.email_host, port=self.port)

        # 发送邮件服务器的对象
        self.smtp.ehlo("smtp.qq.com")
        self.smtp.login(self.username, self.passwd)
        try:
            self.smtp.sendmail(self.username, self.recv, msg.as_string())
            pass
        except Exception as e:
            print('出错了。。', e)
            self.smtp.quit()
            return False
        else:
            print('发送成功！')
            self.smtp.quit()
            return True


def v_code():  # 生成验证码函数
    code = ''
    for i in range(6):
        num = random.randint(0, 9)  # 随机生成0到9的整数
        alf = chr(random.randint(65, 90))  # 根据 ascii码，随机生成字母
        add = random.choice([num, alf])  # 随机返回 num 或者 alf
        code = ''.join([code, str(add)])  # join用于将序列中的元素以指定的字符连接生成一个新的字符串

    return code


def send_verify_email(mail_addr):
    """
    发送邮箱验证码，只需要获取要修改密码人的邮箱，传入函数中即可
    如果成功则返回验证码，如果失败则返回None
    """
    code = v_code()
    m = SendMail(
        username='2625398619@qq.com',
        passwd='yxvjehmvqupmdjhh',
        recv=[mail_addr],
        title='词云图给您的验证',
        content='您的验证码是：' + code + '请您在15分钟内完成密码更改。\n词云图团队',
        ssl=True,   # 必须使用ssl qq把25号端口禁了
    )
    if m.send_mail():
        return code
    else:
        return None


def send_log_email():
    """
    定期运行，向邮箱中发送log日志，不用传参，直接调用即可。
    """
    localtime = time.asctime(time.localtime(time.time()))
    m = SendMail(
        username='2625398619@qq.com',
        passwd='yxvjehmvqupmdjhh',
        recv=['ycx_0320@126.com'],
        title='log info',
        content=localtime + '记录日志',
        file=r'./day.log',  # todo 文件名
        ssl=True,
    )
    m.send_mail()