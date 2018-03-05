import re
import json
import time
import uuid
from lxml import etree
from parse_product_html import SiteType, ParseProduct


def choose_parse(rds, conf, mp, html):
    mapping = eval(mp)
    entry = int(mapping['entry'])
    sel = etree.HTML(html)
    if entry in (conf.LIST, conf.KEY):
        items = sel.xpath('//ul[starts-with(@class, "s-result")]/li[@data-asin]')
        if items:
            parse_list(rds, conf, mp, html)
        else:
            rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
    elif entry in (conf.BEST, conf.NEW):
        items_1 = sel.xpath('//div[starts-with(@class, "zg_itemImmersion")]')
        items_2 = sel.xpath('//div[starts-with(@class, "zg_itemRow")]')  # 日站
        if items_1 or items_2:
            parse_top(rds, conf, mp, html)
        else:
            rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
    else:
        parse_product(rds, conf, mp, html)


def parse_list(rds, conf, mp, html):
    pass


def parse_top(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    entry = mapping['entry']
    category_url = mapping.get('category_url', None)
    task_category = mapping.get('task_category', None)
    if not category_url:
        category_url = page_url
        mapping['category_url'] = page_url

    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]
    domain = SiteType[suffix]
    sign = domain['sign']
    currency = domain['currency']
    sel = etree.HTML(html)

    category = sel.xpath('//h1[@id="zg_listTitle"]/span/text()')
    if category:
        category = category[0].strip()
    else:
        category = ''
    if task_category:
        category = task_category
    products_lst_1 = sel.xpath('//div[starts-with(@class, "zg_itemImmersion")]')  # 美英法站
    products_lst_2 = sel.xpath('//div[starts-with(@class, "zg_itemRow")]')  # 日站
    products_lst = products_lst_1 if products_lst_1 else products_lst_2
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for pl in products_lst:
        # asin
        asin = pl.xpath('.//div[@data-p13n-asin-metadata]/@data-p13n-asin-metadata')
        if asin:
            asin = eval(asin[0])['asin']
            product_url = 'https://www.amazon.{}/dp/{}'.format(suffix, asin)
            rank = pl.xpath('.//span[@class="zg_rankNumber"]/text()')
            if rank:
                rank = rank[0].strip().replace('.', '')
            else:
                rank = 0

            # 类目加asin
            cate_asin = '{}@{}@{}@{}'.format(category, entry, suffix, asin)
            rds.add_set(conf.REDIS_CATE_ASIN, cate_asin)

            # 唯一asin
            unique_asin = '{}@{}'.format(asin, suffix)
            if rds.is_member(conf.REDIS_UNIQUE_ASIN, unique_asin):
                repeat_mp = {'page_url': product_url, 'entry': 1, 'rank': rank, 'category_info': category,
                             'category_url': category_url, 'category_entry': entry, 'create_time': create_time}
                rds.rds.lpush(conf.REDIS_REPEAT_ASIN, repeat_mp)
                print('repeat asin')
                continue
            rds.add_set(conf.REDIS_UNIQUE_ASIN, unique_asin)
            try:
                price_1 = pl.xpath('.//span[starts-with(@class, "a-size-base a-color-price")]/span/text()')
                if price_1:
                    _price = ''.join(price_1).replace(sign, '').replace(currency, '').replace(' ', '').replace(
                        '\xa0', '')
                    if currency == 'EUR':
                        _price = _price.replace('.', '').replace(',', '.')
                    else:
                        _price = _price.replace(',', '')
                    if '-' in _price:
                        price, max_price = [p.strip() for p in _price.split('-')]
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                    else:
                        price = _price
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = 0
                else:
                    price = 0
                    max_price = 0

                price = float(price)
                max_price = float(max_price)
            except:
                price = 0
                max_price = 0
            new_mp = {'page_url': product_url, 'entry': 1, 'rank': rank, 'price': price,
                      'max_price': max_price, 'category_info': category, 'category_url': category_url,
                      'category_entry': entry, 'create_time': create_time}
            rds.rds.rpush('amazon:di:cy:detail', new_mp)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)

    # 判断是否有下一页
    current_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li[contains(@class, "zg_page zg_selected")]/a/@page')
    if current_page:
        current_page_num = current_page[0].strip()
        if current_page_num.isdigit():
            next_page_id = int(current_page_num) + 1
            next_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li/a[@page="%s"]/@href' % next_page_id)
            if next_page:
                next_page_url = next_page[0].strip()
                mapping['page_url'] = next_page_url
                rds.rds.lpush(conf.REDIS_START_URLS, mapping)


def parse_product(rds, conf, mp, html):
    mapping = eval(mp)  # eval()函数还原存入字典值的类型
    page_url = mapping['page_url']
    entry = mapping['entry']
    category_info = mapping.get('category_info', '')
    category_url = mapping.get('category_url', '')
    category_entry = mapping.get('category_entry', entry)
    search_box = mapping.get('search_box', '')
    p_create_time = mapping.get('create_time', None)

    # 确定站点
    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]

    # 以下为传入字段
    product_url = page_url
    products_id = re.findall(r'dp/(.+)', page_url)[0]
    _uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, products_id + suffix)).replace('-', '')
    favornum = mapping.get('rank', 0)
    if int(category_entry) == 2:
        tags = 'List'
    elif int(category_entry) == 3:
        tags = 'KeyWord'
    elif int(category_entry) == 4:
        tags = 'BestSellers'
    elif int(category_entry) == 5:
        tags = 'NewReleases'
    else:
        tags = 'Detail'

    # 以下为页面解析字段
    product = ParseProduct(html, suffix)

    _name = product.get_title()
    if not _name:  # 舍弃没有标题的产品
        rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
        #collect_error(rds, conf, mp, error='No product name')
        return

    currency = product.get_currency()

    first_title = product.get_first_title()

    second_title = ''
    if category_entry == 1:
        category = first_title
    elif category_entry == 3:
        second_title = category_info
        if search_box:
            category = search_box
        else:
            category = first_title
    else:
        category = category_info

    url_id = product.get_asin()

    brand = product.get_brand()

    discount = product.get_discount()

    original_price = product.get_original_price()
    if int(original_price) == 0:
        original_price = mapping.get('original_price', 0)

    price, max_price = product.get_price_maxprice()
    if int(price) == 0:
        price = mapping.get('price', 0)
    if int(max_price) == 0:
        max_price = mapping.get('max_price', 0)

    grade_count = product.get_grade_count()

    review_count = product.get_review_count()

    questions = product.get_questions()

    attribute = product.get_attribute()

    main_image_url = product.get_main_image()

    extra_image_urls = product.get_extra_images()

    if not main_image_url and extra_image_urls:
        main_image_url = extra_image_urls.split(',')[0]

    description = product.get_description()

    generation_time = product.get_generations_time()

    shop_name, shop_url = product.get_shop()

    reserve_field_1 = product.get_reserve_1()

    reserve_field_2 = product.get_reserve_2()

    reserve_field_3 = product.get_reserve_3()

    reserve_field_4 = product.get_reserve_4()

    reserve_field_5 = product.get_reserve_5()

    reserve_field_6, reserve_field_7 = product.get_reserve_6_7()

    if p_create_time:
        create_time = p_create_time
        crawl_time = p_create_time.split()[0]
    else:
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        crawl_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 以下为无需处理字段
    platform = 'amazon'
    platform_url = suffix
    dispatch = ''
    shipping = ''
    version_urls = ''
    sales_total = ''
    total_inventory = ''
    status = 0
    is_delete = 0

    if category_entry in (conf.BEST, conf.NEW):
        table_name = conf.MYSQL_TABLE_SKU_TRACK
    else:
        table_name = conf.MYSQL_TABLE_SKU
    sku_mp = {
            'scgs_uuid': _uuid,
            'scgs_products_id': products_id,
            'scgs_url_id': url_id,
            'scgs_brand': brand,
            'scgs_product_url': product_url,
            'scgs_name': _name,
            'scgs_firstTitle': first_title,
            'scgs_secondTitle': second_title,
            'scgs_original_price': original_price,
            'scgs_price': price,
            'scgs_max_price': max_price,
            'scgs_discount': discount,
            'scgs_dispatch': dispatch,
            'scgs_shipping': shipping,
            'scgs_currency': currency,
            'scgs_attribute': attribute,
            'scgs_version_urls': version_urls,
            'scgs_review_count': review_count,
            'scgs_grade_count': grade_count,
            'scgs_sales_total': sales_total,
            'scgs_total_inventory': total_inventory,
            'scgs_favornum': favornum,
            'scgs_image_url': main_image_url,
            'scgs_extra_image_urls': extra_image_urls,
            'scgs_description': description,
            'scgs_category': category,
            'scgs_category_url': category_url,
            'scgs_tags': tags,
            'scgs_shop_name': shop_name,
            'scgs_shop_url': shop_url,
            'scgs_generation_time': generation_time,
            'scgs_platform': platform,
            'scgs_platform_url': platform_url,
            'scgs_crawl_time': crawl_time,
            'scgs_create_time': create_time,
            'scgs_status': status,
            'scgs_questions': questions,
            'scgs_is_delete': is_delete,
            'scgs_reserve_field_1': reserve_field_1,
            'scgs_reserve_field_2': reserve_field_2,
            'scgs_reserve_field_3': reserve_field_3,
            'scgs_reserve_field_4': reserve_field_4,
            'scgs_reserve_field_5': reserve_field_5,
            'scgs_reserve_field_6': reserve_field_6,
            'scgs_reserve_field_7': reserve_field_7,
        }
    hash_key = '{}{}'.format(conf.REDIS_GENERATION_TIME, suffix)
    if generation_time != '1900-01-01':
        rds.set_hash(hash_key, {products_id: generation_time})
    else:
        exist_generation_time = rds.get_hash_field(hash_key, products_id)
        if exist_generation_time:
            sku_mp['scgs_generation_time'] = exist_generation_time

    data_mp = {"table": table_name, "data": sku_mp}
    push_data_into_redis(rds, conf, data_mp)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def collect_error(rds, conf, mp, **kwargs):
    mapping = eval(mp)
    mapping["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    mapping.update(kwargs)
    rds.add_set(conf.REDIS_ERROR_URLS, mapping)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def push_data_into_redis(rds, conf, data_mp):
    data_json = json.dumps(data_mp)
    rds.rds.lpush(conf.REDIS_DATA_LIST, data_json)
