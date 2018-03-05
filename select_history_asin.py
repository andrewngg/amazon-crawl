import time
from store import AmazonRedis, AmazonStorePro
from settings import MYSQL_CONFIG_SERVER, MYSQL_CONFIG_LOCAL
from config import Config


def select_asin(rds):
    store = AmazonStorePro(**MYSQL_CONFIG_SERVER)   # 服务器本地切换
    add_task_cate = ("select wtc_task_category, wtc_task_type from crawler_amazon_track_task "
                     "where wtc_status=%s and wtc_is_delete=%s")
    lines = store.execute_sql(add_task_cate, 1, 0)
    task_cate = 'amazon:di:cy:taskcate'
    for line in lines:
        cate_type = '{}@{}'.format(line['wtc_task_category'], line['wtc_task_type'])
        rds.add_set(task_cate, cate_type)

    sql_select_asin = (
        "select scgs_id, scgs_products_id, scgs_category, scgs_category_url, scgs_generation_time, scgs_platform_url, "
        "scgs_type from crawler_amazon_sku_track_asin where scgs_status=%s and scgs_is_delete=%s ")
    rows = store.execute_sql(sql_select_asin, 1, 0)
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for row in rows:
        task_type = 1
        category_entry = row['scgs_type']
        task_category = row['scgs_category']
        category_url = row['scgs_category_url']
        suffix = row['scgs_platform_url']
        asin = row['scgs_products_id']
        cate_asin = '{}@{}@{}@{}'.format(task_category, category_entry, suffix, asin)
        asin_cate_type = '{}@{}'.format(task_category, category_entry)
        if not rds.is_member(task_cate, asin_cate_type):
            print('category out')
            continue
        if rds.is_member(Config.REDIS_CATE_ASIN, cate_asin):
            print('exist asin')
            continue
        unique_asin = '{}@{}'.format(asin, suffix)
        if rds.is_member(Config.REDIS_UNIQUE_ASIN, unique_asin):
            product_url = 'https://www.amazon.{}/dp/{}'.format(suffix, asin)
            repeat_mp = {'page_url': product_url, 'entry': 1, 'rank': 101, 'category_info': task_category,
                         'category_url': category_url, 'category_entry': category_entry, 'create_time': create_time}
            rds.rds.lpush(Config.REDIS_REPEAT_ASIN, repeat_mp)
            print('repeat asin')
            rds.add_set(Config.REDIS_CATE_ASIN, cate_asin)
            continue
        rds.add_set(Config.REDIS_CATE_ASIN, cate_asin)
        print(row['scgs_id'])

        page_url = 'https://www.amazon.{}/dp/{}'.format(suffix, asin)
        mp = {'entry': task_type, 'page_url': page_url, 'category_info': task_category, 'category_entry': category_entry,
              'category_url': category_url, 'rank': 101, 'create_time': create_time}
        rds.rds.rpush('amazon:di:cy:detail', mp)
    store.close()


if __name__ == '__main__':
    rds = AmazonRedis()
    today = time.strftime("%Y-%m-%d")
    asin_today = rds.get_hash_field('amazon:di:cy:asin:markdate', 'today')
    if asin_today:
        asin_today = asin_today.split()[0]
    if asin_today == today:
        print('toady finish')
    else:
        list_today = rds.get_hash_field('amazon:di:cy:lc:markdate', 'today')
        if list_today:
            list_today = list_today.split()[0]
        if list_today == today:
            rds.set_hash('amazon:di:cy:asin:markdate', {'today': time.strftime("%Y-%m-%d %H:%M:%S")})
            print('scan_database')
            select_asin(rds)
            rds.delete_key(Config.REDIS_CATE_ASIN)
            rds.delete_key(Config.REDIS_UNIQUE_ASIN)
            rds.delete_key('amazon:di:cy:taskcate')









