import asyncio
import time
import queue
from config import Config
from crawl_func import clear_rds, start_crawl, start_thread
from store import AmazonRedis
from scan_task import scan_database


class ConfigSub(Config):
    REDIS_START_URLS_NAME = 'list'
    REDIS_SUB_DIR_NAME = 'lc'


if __name__ == '__main__':
    conf = ConfigSub()
    que = queue.Queue()
    rds = AmazonRedis()

    clear_rds(rds, conf)

    sign = scan_database(rds, conf)
    if sign:
        rds.delete_key('amazon:di:cy:dc01:markdate')

    new_loop = asyncio.new_event_loop()

    start_thread(new_loop)

    try:
        while True:
            start_crawl(rds, que, conf, new_loop)
            # 队列都为空，采集完成
            if not rds.exists_key(conf.REDIS_START_URLS) and not rds.exists_key(conf.REDIS_REQUEST_URLS) and not rds.exists_key(conf.REDIS_CRAWL_URLS):
                finish_time = time.strftime("%Y-%m-%d %H:%M:%S")
                rds.set_hash(conf.REDIS_SUB_DIR + 'markdate', {'today': finish_time})
                break
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        new_loop.stop()



