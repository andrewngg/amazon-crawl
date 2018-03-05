
class Config:
    # mysql表名
    MYSQL_TABLE_SKU = 'crawler_amazon_sku'
    MYSQL_TABLE_SKU_TRACK = 'crawler_amazon_sku_track'

    # 任务标签分类
    DETAIL = 1
    LIST = 2
    KEY = 3
    BEST = 4
    NEW = 5

    # 并发数
    CONCURRENT = 100

    # 代理
    REMAIN = 10
    FAIL_TIMES = 2

    # 超时
    TIMEOUT = 50

    # redis目录设置
    REDIS_DIR = 'amazon:di:cy:'
    REDIS_DATA_LIST = '{}datalist'.format(REDIS_DIR)
    REDIS_DATA_ERROR = '{}dataerror'.format(REDIS_DIR)
    REDIS_CATE_ASIN = '{}cateasin'.format(REDIS_DIR)
    REDIS_UNIQUE_ASIN = '{}uniqueasin'.format(REDIS_DIR)
    REDIS_REPEAT_ASIN = '{}repeatasin'.format(REDIS_DIR)
    REDIS_GENERATION_TIME = 'amazon:di:generationtime:'
    REDIS_SUB_DIR_NAME = 'base'
    REDIS_START_URLS_NAME = 'base'

    def __init__(self):
        self.REDIS_START_URLS = '{dir}{start_url_name}'.format(dir=self.REDIS_DIR, start_url_name=self.REDIS_START_URLS_NAME)

        self.REDIS_SUB_DIR = '{dir}{sub_dir_name}:'.format(dir=self.REDIS_DIR, sub_dir_name=self.REDIS_SUB_DIR_NAME)
        self.REDIS_REQUEST_URLS = '{}request'.format(self.REDIS_SUB_DIR)
        self.REDIS_CRAWL_URLS = '{}crawl'.format(self.REDIS_SUB_DIR)
        self.REDIS_ERROR_URLS = '{}error'.format(self.REDIS_SUB_DIR)


if __name__ == '__main__':
    pass
