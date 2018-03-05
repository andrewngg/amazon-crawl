import time
import sys
from store import AmazonRedis
from send_email import SendEmail

if __name__ == '__main__':
    rds = AmazonRedis()
    mail_today = rds.get_hash_field('amazon:di:cy:mail', 'today')
    detail_today = rds.get_hash_field('amazon:di:cy:dc01:markdate', 'today')
    if detail_today:
        detail_today = detail_today.split()[0]
    today = time.strftime("%Y-%m-%d")
    if mail_today == today:
        print('DI finish')
        sys.exit()
    if detail_today == today and not rds.exists_key('amazon:di:cy:repeatasin'):
        email = SendEmail()
        context = 'ok'
        email.send_message('DI', 'chenyang@banggood.com', '今日采集完成', context)
        today_date = time.strftime("%Y-%m-%d")
        rds.set_hash('amazon:di:cy:mail', {'today': today_date})
    else:
        print('DI no finish')
