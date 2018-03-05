# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from smtplib import SMTP_SSL
import traceback


class SendEmail:
    def __init__(self):
        self.smtp_server = 'smtp.exmail.qq.com'
        self.smtp_port = 465
        self.from_addr = 'chenyang@banggood.com'
        self.password = 'TV9Lq3ddSe6k4rcG'

    def format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_message(self, prefix, to_addr, head, message):
        try:
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['From'] = self.format_addr(u'%s <%s>' % (prefix, self.from_addr))
            msg['To'] = self.format_addr(u'<%s>' % to_addr)
            msg['Subject'] = Header(head, 'utf-8').encode()
            server = SMTP_SSL(self.smtp_server, self.smtp_port)
            #server.set_debuglevel(1)
            server.login(self.from_addr, self.password)
            server.sendmail(self.from_addr, [to_addr], msg.as_string())
            server.quit()

            print('send email successfully')
        except:
            print('send email failed')
            traceback.print_exc()


if __name__ == '__main__':

    send_email = SendEmail()
    context = 'ok'
    send_email.send_message('DI', 'chenyang@banggood.com', '今日采集完成', context)


