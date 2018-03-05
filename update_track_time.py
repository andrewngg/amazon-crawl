import time
from store import AmazonStorePro
from settings import MYSQL_CONFIG_SERVER
from send_email import SendEmail
import datetime

sql_asin = "update crawler_amazon_track_task set wtc_crawl_time=%s where wtc_status=1"


def update_time(ut):
    store = AmazonStorePro(**MYSQL_CONFIG_SERVER)   # 服务器本地切换
    store.execute_sql(sql_asin, ut)
    store.close()


if __name__ == '__main__':
    crawl_time = '23:50:55'
    crawl_date_time = '{} {}'.format(time.strftime("%Y-%m-%d"), crawl_time)
    crawl_date = datetime.datetime.strptime(crawl_date_time, "%Y-%m-%d %H:%M:%S")
    set_crawl_date = crawl_date - datetime.timedelta(days=1)
    print(set_crawl_date)
    update_time(set_crawl_date)
    send_email = SendEmail()
    context = '采集任务时间设置为: {}'.format(set_crawl_date)
    send_email.send_message('设置任务采集时间', 'chenyang@banggood.com', '成功设置任务采集时间', context)
