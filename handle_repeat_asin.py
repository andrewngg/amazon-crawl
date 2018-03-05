import json
import time
import re
from store import AmazonRedis, AmazonStorePro
from settings import MYSQL_CONFIG_SERVER, MYSQL_CONFIG_LOCAL
from config import Config

sql_select_asin = ("select scgs_uuid, scgs_url_id, scgs_brand, scgs_name, scgs_firstTitle, scgs_secondTitle, "
                   "scgs_original_price, scgs_price, scgs_max_price, scgs_discount, scgs_attribute, scgs_review_count, "
                   "scgs_grade_count, scgs_image_url, scgs_extra_image_urls, scgs_description, scgs_shop_name, "
                   "scgs_shop_url, scgs_generation_time, scgs_questions, scgs_currency, "
                   "scgs_reserve_field_1, scgs_reserve_field_2, scgs_reserve_field_3, scgs_reserve_field_4, "
                   "scgs_reserve_field_5, scgs_reserve_field_6, scgs_reserve_field_7 from crawler_amazon_sku_track "
                   "where scgs_products_id=%s and scgs_platform_url=%s order by scgs_id desc limit 1")


def select_asin(rds):
    if rds.exists_key(Config.REDIS_REPEAT_ASIN):
        store = AmazonStorePro(**MYSQL_CONFIG_SERVER)  # 服务器本地切换
        while rds.exists_key(Config.REDIS_REPEAT_ASIN):
            item = rds.rds.rpop(Config.REDIS_REPEAT_ASIN)
            asin_mp = eval(item)
            product_url = asin_mp['page_url']
            asin = re.findall(r'dp/(.+)', product_url)[0]
            print(asin)
            rank = asin_mp['rank']
            category = asin_mp['category_info']
            category_entry = asin_mp['category_entry']
            create_time = asin_mp['create_time']
            category_url = asin_mp['category_url']
            suffix = re.findall(r'www.amazon.(.*?)/', category_url)[0]
            if int(category_entry) == 4:
                tags = 'BestSellers'
            else:
                tags = 'NewReleases'

            crawl_time = create_time.split()[0]
            rst = store.execute_sql(sql_select_asin, asin, suffix)
            if rst:
                rst = rst[0]
                sku_mp = {
                    'scgs_uuid': rst['scgs_uuid'],
                    'scgs_products_id': asin,
                    'scgs_url_id': rst['scgs_url_id'],
                    'scgs_brand': rst['scgs_brand'],
                    'scgs_product_url': product_url,
                    'scgs_name': rst['scgs_name'],
                    'scgs_firstTitle': rst['scgs_firstTitle'],
                    'scgs_secondTitle': rst['scgs_secondTitle'],
                    'scgs_original_price': rst['scgs_original_price'],
                    'scgs_price': rst['scgs_price'],
                    'scgs_max_price': rst['scgs_max_price'],
                    'scgs_discount': rst['scgs_discount'],
                    'scgs_dispatch': '',
                    'scgs_shipping': '',
                    'scgs_currency': rst['scgs_currency'],
                    'scgs_attribute': rst['scgs_attribute'],
                    'scgs_version_urls': '',
                    'scgs_review_count': rst['scgs_review_count'],
                    'scgs_grade_count': rst['scgs_grade_count'],
                    'scgs_sales_total': '',
                    'scgs_total_inventory': '',
                    'scgs_favornum': rank,
                    'scgs_image_url': rst['scgs_image_url'],
                    'scgs_extra_image_urls': rst['scgs_extra_image_urls'],
                    'scgs_description': rst['scgs_description'],
                    'scgs_category': category,
                    'scgs_category_url': category_url,
                    'scgs_tags': tags,
                    'scgs_shop_name': rst['scgs_shop_name'],
                    'scgs_shop_url': rst['scgs_shop_url'],
                    'scgs_generation_time': rst['scgs_generation_time'].strftime("%Y-%m-%d"),
                    'scgs_platform': 'amazon',
                    'scgs_platform_url': suffix,
                    'scgs_crawl_time': crawl_time,
                    'scgs_create_time': create_time,
                    'scgs_status': 0,
                    'scgs_questions': rst['scgs_questions'],
                    'scgs_is_delete': 0,
                    'scgs_reserve_field_1': rst['scgs_reserve_field_1'],
                    'scgs_reserve_field_2': rst['scgs_reserve_field_2'],
                    'scgs_reserve_field_3': rst['scgs_reserve_field_3'],
                    'scgs_reserve_field_4': rst['scgs_reserve_field_4'],
                    'scgs_reserve_field_5': rst['scgs_reserve_field_5'],
                    'scgs_reserve_field_6': rst['scgs_reserve_field_6'],
                    'scgs_reserve_field_7': rst['scgs_reserve_field_7'],
                }
                data_mp = {"table": Config.MYSQL_TABLE_SKU_TRACK, "data": sku_mp}
                push_data_into_redis(rds, Config, data_mp)
            else:
                print('no exist asin')

        print('push repeat done')
        store.close()
    else:
        print('no repeat asin')


def push_data_into_redis(rds, conf, data_mp):
    data_json = json.dumps(data_mp)
    rds.rds.lpush(conf.REDIS_DATA_LIST, data_json)


if __name__ == '__main__':
    rds = AmazonRedis()
    detail_today = rds.get_hash_field('amazon:di:cy:dc01:markdate', 'today')
    if detail_today:
        detail_today = detail_today.split()[0]
    today = time.strftime("%Y-%m-%d")
    if detail_today == today:
        print('start handling repeat asin')
        select_asin(rds)
    else:
        print('wait for detail finish')




