import json
import time
import traceback
from store import AmazonStorePro, AmazonRedis
from settings import MYSQL_CONFIG_LOCAL, MYSQL_CONFIG_SERVER
from config import Config

sql_sku = (
    "insert into {}(scgs_uuid, scgs_products_id, scgs_url_id, scgs_brand, scgs_product_url, scgs_name,"
    "scgs_firstTitle, scgs_secondTitle, scgs_original_price, scgs_price, scgs_max_price, scgs_discount,"
    "scgs_dispatch, scgs_shipping, scgs_currency, scgs_attribute, scgs_version_urls, scgs_review_count,"
    "scgs_grade_count, scgs_sales_total, scgs_total_inventory, scgs_favornum, scgs_image_url,"
    "scgs_extra_image_urls, scgs_description, scgs_category, scgs_category_url, scgs_tags, scgs_shop_name, "
    "scgs_shop_url, scgs_generation_time, scgs_platform, scgs_platform_url, scgs_crawl_time, scgs_create_time, "
    "scgs_status, scgs_questions, scgs_is_delete, scgs_reserve_field_1, scgs_reserve_field_2,"
    "scgs_reserve_field_3, scgs_reserve_field_4, scgs_reserve_field_5, scgs_reserve_field_6,"
    "scgs_reserve_field_7)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
    "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")


def data_insert(rds):
    if rds.exists_key(Config.REDIS_DATA_LIST):
        store = AmazonStorePro(**MYSQL_CONFIG_SERVER)   # 服务器本地切换
        while rds.exists_key(Config.REDIS_DATA_LIST):
            item = rds.rds.rpop(Config.REDIS_DATA_LIST)
            item_json = json.loads(item)
            table = item_json['table']
            print(table)
            data = item_json['data']
            try:
                if table == Config.MYSQL_TABLE_SKU_TRACK:
                    store.execute_sql(sql_sku.format(table),
                                      data['scgs_uuid'],
                                      data['scgs_products_id'],
                                      data['scgs_url_id'],
                                      data['scgs_brand'],
                                      data['scgs_product_url'],
                                      data['scgs_name'],
                                      data['scgs_firstTitle'],
                                      data['scgs_secondTitle'],
                                      data['scgs_original_price'],
                                      data['scgs_price'],
                                      data['scgs_max_price'],
                                      data['scgs_discount'],
                                      data['scgs_dispatch'],
                                      data['scgs_shipping'],
                                      data['scgs_currency'],
                                      data['scgs_attribute'],
                                      data['scgs_version_urls'],
                                      data['scgs_review_count'],
                                      data['scgs_grade_count'],
                                      data['scgs_sales_total'],
                                      data['scgs_total_inventory'],
                                      data['scgs_favornum'],
                                      data['scgs_image_url'],
                                      data['scgs_extra_image_urls'],
                                      data['scgs_description'],
                                      data['scgs_category'],
                                      data['scgs_category_url'],
                                      data['scgs_tags'],
                                      data['scgs_shop_name'],
                                      data['scgs_shop_url'],
                                      data['scgs_generation_time'],
                                      data['scgs_platform'],
                                      data['scgs_platform_url'],
                                      data['scgs_crawl_time'],
                                      data['scgs_create_time'],
                                      data['scgs_status'],
                                      data['scgs_questions'],
                                      data['scgs_is_delete'],
                                      data['scgs_reserve_field_1'],
                                      data['scgs_reserve_field_2'],
                                      data['scgs_reserve_field_3'],
                                      data['scgs_reserve_field_4'],
                                      data['scgs_reserve_field_5'],
                                      data['scgs_reserve_field_6'],
                                      data['scgs_reserve_field_7'])

            except Exception as exp:
                traceback.print_exc()
                item_json['error'] = '{!r}'.format(exp)
                rds.rds.lpush(Config.REDIS_DATA_ERROR, json.dumps(item_json))

        print('finished insert')
        store.close()
    else:
        print('no item')
        time.sleep(30)


if __name__ == '__main__':
    rds = AmazonRedis()
    while True:
        data_insert(rds)
