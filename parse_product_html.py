import re
import datetime
import json
from lxml import etree

# 采集站点：美、英、日、法、意、西、德、印、加站
SiteType = {
    'com': {'site': 'https://www.amazon.com', 'currency': 'USD', 'sign': '$'},
    'co.uk': {'site': 'https://www.amazon.co.uk', 'currency': 'GBP', 'sign': '£'},
    'co.jp': {'site': 'https://www.amazon.co.jp', 'currency': 'YEN', 'sign': '￥'},
    'fr': {'site': 'https://www.amazon.fr', 'currency': 'EUR', 'sign': 'EUR'},
    'it': {'site': 'https://www.amazon.it', 'currency': 'EUR', 'sign': 'EUR'},
    'es': {'site': 'https://www.amazon.es', 'currency': 'EUR', 'sign': 'EUR'},
    'de': {'site': 'https://www.amazon.de', 'currency': 'EUR', 'sign': 'EUR'},
    'in': {'site': 'https://www.amazon.in', 'currency': 'INR', 'sign': ''},
    'ca': {'site': 'https://www.amazon.ca', 'currency': 'CDN', 'sign': '$'},
}

# 上架日期
Month = {
    'com': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'],
            'xpath_text': 'Date first available'},
    'co.uk': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'],
              'xpath_text': 'Date First Available'},
    'co.jp': {'xpath_text': 'での取り扱い開始日'},         # 日站的时间格式是数字形式的
    'fr': {'month': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
           'xpath_text': 'Date de mise en ligne sur Amazon.fr'},
    'it': {'month': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                     'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
           'xpath_text': 'Disponibile su Amazon.it a partire dal'},
    'es': {'month': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'noviembre', 'Diciembre'],
           'xpath_text': 'Producto en Amazon.es desde'},
    'de': {'month': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                     'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
           'xpath_text': 'Im Angebot von Amazon.de seit'},
    'in': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'],
           'xpath_text': 'Date first available'},
    'ca': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'],
           'xpath_text': 'Date first available'},
}


class ParseProduct:
    """
    解析亚马逊产品详情页
    实例化类时传入参数：
    html：详情页html文本
    suffix：站点类型('com', 'co.uk', 'co.jp', 'fr', 'it', 'es', 'de', 'in', 'ca')
    类方法get_xxx()返回解析得到的相应字段值
    """

    def __init__(self, html, suffix):
        self.sel = etree.HTML(html)
        self.suffix = suffix

    # 产品标题
    def get_title(self):
        title_1 = self.sel.xpath('//span[@id="productTitle"]/text()')
        title_2 = self.sel.xpath('//div[@id="title_feature_div"]/h1/text()')
        title_3 = self.sel.xpath('//div[@id="mnbaProductTitleAndYear"]/span/text()')
        title_4 = self.sel.xpath('//h1[starts-with(@class, "parseasinTitle")]/span/text()')
        title_5 = self.sel.xpath('//span[@id="ebooksProductTitle"]/text()')
        title_6 = self.sel.xpath('//div[contains(@id,"Title")]//h1/text()')
        if title_1:
            title = title_1[0].strip()
        elif title_2:
            title = title_2[0].strip()
        elif title_3:
            title = ''.join(title_3)
        elif title_4:
            title = title_4[0].strip()
        elif title_5:
            title = title_5[0].strip()
        elif title_6:
            title = title_6[0].strip()
        else:
            title = ''
        return title

    def get_currency(self):
        return SiteType[self.suffix]['currency']

    # 产品类目
    def get_first_title(self):
        page_category = self.sel.xpath('//div[starts-with(@id, "wayfinding-breadcrumbs_feature_div")]//li//a/text()')
        if page_category:
            first_title = '>'.join([item.strip() for item in page_category])
        else:
            first_title = ''
        return first_title

    # 产品asin
    def get_asin(self):
        asin_1 = self.sel.xpath('//th[contains(text(), "ASIN:")]/../*[2]/text()')
        asin_2 = self.sel.xpath('//td[contains(text(), "ASIN:")]/../*[2]/text()')
        asin_3 = self.sel.xpath('//b[contains(text(), "ASIN:")]/../text()')
        asin_4 = self.sel.xpath('//span[contains(text(), "ASIN:")]/../*[2]/text()')
        if asin_1:
            asin = asin_1
        elif asin_2:
            asin = asin_2
        elif asin_3:
            asin = asin_3
        elif asin_4:
            asin = asin_4
        else:
            asin = ''
        if asin:
            asin = asin[0].strip()
            if len(asin) > 10:
                asin = ''
        return asin

    # 品牌
    def get_brand(self):
        brand_1 = self.sel.xpath('//a[@id="bylineInfo"]/text()')
        brand_2 = self.sel.xpath('//a[@id="brand"]/text()')
        brand_3 = self.sel.xpath('//th[contains(text(), "Brand")]')
        brand_4 = self.sel.xpath('//div[@id="center-col"]/div[contains(@class, "buying")]/span/a/text()')
        if brand_1:
            brand = brand_1[0].strip()
        elif brand_2:
            brand = brand_2[0].strip()
        elif brand_3:
            brand = brand_3[0].xpath('./../td/text()')
            if brand:
                brand = brand[0].strip()
            else:
                brand = ''
        elif brand_4:
            brand = brand_4[0].strip()
        else:
            brand = ''
        return brand

    # 折扣
    def get_discount(self):
        discount = self.sel.xpath('//*[contains(@id, "price_savings")]/*[2]/text()')
        if discount:
            discount_num = re.findall(r'(\d+)%', discount[0]) if '%' in discount[0] else re.findall(r'(\d+)',
                                                                                                    discount[0])
            if discount_num:
                discount_num = discount_num[0]
                discount = str(100 - int(discount_num)) + '%'
            else:
                discount = ''
        else:
            discount = ''
        return discount

    # 原价
    def get_original_price(self):
        domain = SiteType[self.suffix]
        currency = domain['currency']
        sign = domain['sign']
        original_price = self.sel.xpath('//div[@id="price"]//span[@class="a-text-strike"]/text()')
        if original_price:
            original_price = original_price[0].strip().replace(sign, '').replace(currency, '').replace(' ', '').replace(
                '\xa0', '')
            if currency == 'EUR':
                original_price = original_price.replace('.', '').replace(',', '.')
            else:
                original_price = original_price.replace(',', '')
        else:
            original_price = 0

        try:
            original_price = float(original_price)
        except (ValueError, TypeError):
            print('get_original_price raise exception')
            original_price = 0
        return original_price

    # 售价和最高价
    def get_price_maxprice(self):
        domain = SiteType[self.suffix]
        currency = domain['currency']
        sign = domain['sign']
        price_1 = self.sel.xpath('//span[contains(@id, "priceblock")]/text()')
        price_2 = self.sel.xpath('//div[@id="centerCol"]//span[@id="color_name_1_price"]/span/text()')
        price_3 = self.sel.xpath('//span[@id="actualPriceValue"]//text()')
        price_4 = self.sel.xpath('//span[contains(@id, "priceblock")]/span[contains(@class, "buyingPrice")]/text()')
        price_5 = self.sel.xpath('//span[@id="vas-offer-price-0"]/text()')
        price_6 = self.sel.xpath('//span[@class="guild_priceblock_value a-hidden"]/text()')
        price_7 = self.sel.xpath('//div[@class="inlineBlock-display"]/span[contains(@class,"a-size-medium a-color-price offer-price a-text-normal")]/text()')
        if price_1 and price_1[0].strip():
            price = price_1[0].strip().replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            if currency == 'EUR':
                price = price.replace('.', '').replace(',', '.')
            else:
                price = price.replace(',', '')
            if '-' in price:
                price, max_price = [p.strip() for p in price.split('-')]
                price = re.findall(r'\d+\.?\d*', price)
                if price:
                    price = ''.join(price)
                else:
                    price = 0
                max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                if max_price:
                    max_price = ''.join(max_price)
                else:
                    max_price = 0
            else:
                max_price = 0
        elif price_2:
            price = ''.join(price_2).replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            if 'from' not in price:
                if currency == 'EUR':
                    price = price.replace('.', '').replace(',', '.')
                else:
                    price = price.replace(',', '')
                price = re.findall(r'\d+\.?\d*', price)
                if price:
                    price = ''.join(price)
                else:
                    price = 0
            else:
                price = 0
            max_price = 0
        elif price_3:
            price = ''.join([item.strip().replace(sign, '') for item in price_3])
            max_price = 0
        elif price_4:
            price_bg = price_4[0].strip()
            price_sm = '00'
            price_pd = self.sel.xpath(
                '//span[contains(@id, "priceblock")]/span[contains(@class, "priceToPayPadding")]/text()')
            if price_pd:
                price_sm = price_pd[0].strip()
            price = '{}.{}'.format(price_bg, price_sm)
            max_price = 0
        elif price_5:
            price = price_5[0].strip().replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            max_price = 0
        elif price_6:
            price = price_6[0].strip().replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            max_price = 0
        elif price_7:
            price = price_7[0].strip().replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            max_price = 0
        else:
            price = 0
            max_price = 0
        try:
            price = float(price)
        except (ValueError, TypeError):
            print('get_price raise exception')
            price = 0
        try:
            max_price = float(max_price)
        except (ValueError, TypeError):
            print('get_maxprice raise exception')
            max_price = 0
        return price, max_price

    # 评分
    def get_grade_count(self):
        grade_count_1 = self.sel.xpath('//span[@id="acrPopover"]/@title')
        grade_count_2 = self.sel.xpath('//div[@id="vas-reviews"]//div[@id="aggregatedReviews"]/span/text()')
        grade_count_3 = self.sel.xpath('//div[@id="center-col"]//span[contains(text(), "5 stars")]/text()')
        if grade_count_1:
            if self.suffix == 'co.jp':
                grade_count = grade_count_1[0].strip().split(' ')[-1]
            else:
                grade_count = grade_count_1[0].strip().split(' ')[0]
        elif grade_count_2:
            grade_count = grade_count_2[0].strip().split(' ')[0]
        elif grade_count_3:
            grade_count = grade_count_3[0].strip().split(' ')[0]
        else:
            grade_count = 0
        try:
            grade_count = float(grade_count)
        except (ValueError, TypeError):
            print('get_grade_count raise exception')
            grade_count = 0
        return grade_count

    # 评论数
    def get_review_count(self):
        review_count_1 = self.sel.xpath('//span[@id="acrCustomerReviewText"]/text()')
        review_count_2 = self.sel.xpath('//div[@id="vas-reviews"]//div[@id="vasAsinStarRating"]/a[2]/text()')
        review_count_3 = self.sel.xpath('//div[@id="center-col"]//a[contains(text(), "customer reviews")]/text()')
        if review_count_1:
            review_count_1 = review_count_1[0].strip().replace(',', '')
            review_count = re.findall(r'(\d+)', review_count_1)[0]
        elif review_count_2:
            review_count_2 = review_count_2[0].strip().replace(',', '')
            review_count = re.findall(r'(\d+)', review_count_2)[0]
        elif review_count_3:
            review_count_3 = review_count_3[0].strip().replace(',', '')
            review_count = re.findall(r'(\d+)', review_count_3)[0]
        else:
            review_count = 0
        try:
            review_count = int(review_count)
        except (ValueError, TypeError):
            print('get_review_count raise exception')
            review_count = 0
        return review_count

    # 提问数
    def get_questions(self):
        _questions = self.sel.xpath('//a[@id="askATFLink"]/span/text()')
        if _questions:
            _questions = _questions[0].strip().replace('+', '').replace(',', '')
            questions = re.findall(r'\d+', _questions)[0]
        else:
            questions = 0

        try:
            questions = int(questions)
        except (ValueError, TypeError):
            print('get_questions raise exception')
            questions = 0
        return questions

    # 属性
    def get_attribute(self):
        attribute = dict()
        size = self.sel.xpath('//div[@id="variation_size_name"]')
        if size:
            if size[0].xpath('//select[@id="native_dropdown_selected_size_name"]'):
                attribute['size'] = [item.strip() for item in
                                     size[0].xpath(
                                         '//select[@id="native_dropdown_selected_size_name"]/option/text()')[
                                     1:]]
            elif size[0].xpath('//span[@class="selection"]/text()'):
                attribute['size'] = size[0].xpath('//span[@class="selection"]/text()')[0].strip()
            elif size[0].xpath('div/text()'):
                attribute['size'] = ''.join([item.strip() for item in size[0].xpath('div/text()')])

        color = self.sel.xpath('//div[@id="variation_color_name"]')
        if color:
            if color[0].xpath(
                    '//select[@id="native_dropdown_selected_color_name"]//option/@data-a-html-content'):
                attribute['color'] = color[0].xpath(
                    '//select[@id="native_dropdown_selected_color_name"]//option/@data-a-html-content')
            elif color[0].xpath('ul//li/@title'):
                attribute['color'] = [color.replace('Click to select', '').strip() for color in
                                      color[0].xpath('ul//li/@title')]
            elif color[0].xpath('//span[@class="selection"]/text()'):
                attribute['color'] = ''.join(
                    [item.strip() for item in color[0].xpath('//span[@class="selection"]/text()')])
            elif color[0].xpath('div/text()'):
                attribute['color'] = ''.join([item.strip() for item in color[0].xpath('div/text()')])

        style = self.sel.xpath('//div[@id="variation_style_name"]')
        if style:
            style_option = self.sel.xpath(
                '//select[@id="native_dropdown_selected_style_name"]//option/@data-a-html-content')
            style_option_1 = style[0].xpath('.//span/text()')
            if style_option:
                attribute['style'] = style_option
            elif style_option_1:
                attribute['style'] = style_option_1[0].strip()
            else:
                styles = style[0].xpath('ul//li/@title')
                attribute['style'] = [' '.join(style.split(' ')[3:]) for style in styles]

        if attribute:
            attribute = json.dumps(attribute, ensure_ascii=False)
        else:
            attribute = ''
        return attribute

    # 主图
    def get_main_image(self):
        image_url_1 = self.sel.xpath('//img[@id="landingImage" or @id="imgBlkFront"]/@data-a-dynamic-image')
        image_url_2 = self.sel.xpath('//div[@id="coverArt_feature_div"]/img/@src')
        image_url_3 = self.sel.xpath('//div[@id="aud_main_container"]//img/@src')
        image_url_4 = self.sel.xpath('//img[@id="js-masrw-main-image"]/@src')
        image_url_5 = self.sel.xpath('//div[@id="vasBleedImage_feature_div"]/style/text()')
        if image_url_1:
            main_image_url = re.findall(r'{"(.+?)"', image_url_1[0])
            if main_image_url:
                main_image_url = main_image_url[0].strip()
            else:
                main_image_url = ''
        elif image_url_2:
            main_image_url = image_url_2[0].strip()
        elif image_url_3:
            main_image_url = image_url_3[0].strip()
        elif image_url_4:
            main_image_url = image_url_4[0].strip()
        elif image_url_5:
            main_image_url = image_url_5[0].strip()
            main_image_url = re.findall(r'background-image: url\("(.+)"\)', main_image_url)
            if main_image_url:
                main_image_url = main_image_url[0].strip()
            else:
                main_image_url = ''
        else:
            main_image_url = ''
        if not main_image_url.startswith('http'):
            main_image_url = ''
        return main_image_url

    # 小图
    def get_extra_images(self):
        eiu = []
        extra_image_urls_1 = self.sel.xpath('//div[@id="altImages"][1]/ul/li//img/@src')
        extra_image_urls_2 = self.sel.xpath('//ul[@id="gc-design-mini-picker"]/li//img/@src')
        extra_image_urls_3 = self.sel.xpath('//li[@class="a-carousel-card masrw-thumb-card"]/a/img/@src')
        if extra_image_urls_1:
            _extra_image_urls = extra_image_urls_1
        elif extra_image_urls_2:
            _extra_image_urls = extra_image_urls_2
        elif extra_image_urls_3:
            _extra_image_urls = extra_image_urls_3
        else:
            _extra_image_urls = ''
        for url in _extra_image_urls:
            if url.startswith('http'):
                if '.jpg' in url:
                    image_url = re.findall(r'(.+)\._?.+\.jpg', url)[0] + '.jpg'
                    eiu.append(image_url)
                elif '.png' in url:
                    image_url = re.findall(r'(.+)\._?.+\.png', url)[0] + '.png'
                    eiu.append(image_url)
                else:
                    pass
        if eiu:
            extra_image_urls = ','.join(eiu)
        else:
            extra_image_urls = ''
        return extra_image_urls

    # 描述
    def get_description(self):
        description_1 = self.sel.xpath('//div[@id="productDescription"]/p/text()')
        description_2 = self.sel.xpath('//div[@id="mas-product-description"]/div/text()')
        if description_1:
            description = description_1
        elif description_2:
            description = description_2
        else:
            description = ''
        description = ''.join([desc.strip() for desc in description])
        return description

    # 上架日期
    def get_generations_time(self):
        release_date = self.sel.xpath('//*[contains(text(), "Original Release Date")]/../text()')
        if self.suffix in ('com', 'co.uk'):  # 美英站两种匹配规则
            ymd_com = self.sel.xpath('//*[contains(text(), "%s")]' % Month['com']['xpath_text'])
            ymd_uk = self.sel.xpath('//*[contains(text(), "%s")]' % Month['co.uk']['xpath_text'])
            ymd = ymd_com if ymd_com else ymd_uk
        else:
            ymd = self.sel.xpath('//*[contains(text(), "%s")]' % Month[self.suffix]['xpath_text'])
        if ymd or release_date:
            if ymd:
                ymd_1 = ymd[-1].xpath('./../*[2]/text()')
                ymd_2 = ymd[-1].xpath('./../text()')
                ymd_3 = ymd[-1].xpath('./text()')
                if ymd_1 and re.findall(r'\d{4}', ymd_1[0]):
                    ymd = ymd_1
                elif ymd_2 and re.findall(r'\d{4}', ymd_2[0]):
                    ymd = ymd_2
                elif ymd_3:
                    ymd_3_1 = re.findall(r':(.+\d+)', ymd_3[0].strip())
                    ymd_3_2 = re.findall(r'\|(\d{1,2}.+\d{4})\|', ymd_3[0].strip())
                    ymd = ymd_3_1 if ymd_3_1 else ymd_3_2
            else:
                ymd = release_date
            if self.suffix == 'co.jp':  # 日站
                details = ymd[0].strip().split('/')
                generation_time = '%s-%s-%s' % (details[0], details[1], details[2])
            else:
                ymd = ymd[0].strip().replace(',', '').replace('.', '')
                d = re.findall(r'\d{1,2}', ymd)[0]
                y = re.findall(r'\d{4}', ymd)[0]
                m = ymd.replace(y, '').replace(d, '').strip()
                if self.suffix == 'es':
                    m = m.replace('de', '').strip()
                month = self._format_month(m)
                generation_time = '%s-%s-%s' % (y, month, d)
            try:
                generation_date = datetime.datetime.strptime(generation_time, '%Y-%m-%d')
                generation_time = generation_date.strftime('%Y-%m-%d')
            except:
                generation_time = '1900-01-01'
        else:
            generation_time = '1900-01-01'
        return generation_time

    def _format_month(self, m):
        month = Month[self.suffix]['month']
        for index, item in enumerate(month):
            if item.lower().startswith(m.lower()):
                return index+1

    # 店铺
    def get_shop(self):
        domain = SiteType[self.suffix]
        site = domain['site']
        shop = self.sel.xpath('//div[@id="merchant-info"]/a')
        if shop:
            shop_name = self.sel.xpath('//div[@id="merchant-info"]/a/text()')[0]
            shop_url = site + self.sel.xpath('//div[@id="merchant-info"]/a/@href')[0]
        else:
            shop_name = ''
            shop_url = ''
        return shop_name, shop_url

    # 评分百分比
    def get_reserve_1(self):
        histogram_review_count = dict()
        histogram_review_count_1 = self.sel.xpath('//div[starts-with(@id, "rev")]//tr[contains(@class, "histogram-row")]')
        histogram_review_count_2 = self.sel.xpath('//div[@id="aggregatedReviews"]/table[@id="histogramTable"]//tr[contains(@class, "histogram-row")]')
        if histogram_review_count_1:
            _histogram_review_count = histogram_review_count_1
        elif histogram_review_count_2:
            _histogram_review_count = histogram_review_count_2
        else:
            _histogram_review_count = ''
        for h in _histogram_review_count[:5]:
            star_1 = h.xpath('./td[1]/*[1]/text()')
            star_2 = h.xpath('./td[1]/text()')
            if star_1:
                _star = star_1[0]
            else:
                _star = star_2[0]
            star = re.findall(r'\d', _star)[0]
            percent_1 = h.xpath('./td[3]//text()')   # 更精确
            percent_2 = h.xpath('.//div[contains(@class, "a-meter") and @aria-label]/@aria-label')
            if percent_1:
                percent = percent_1[0].strip()
            elif percent_2:
                percent = percent_2[0].strip()
            else:
                percent = '0%'
            histogram_review_count[star] = percent
        if histogram_review_count:
            histogram_review_count = json.dumps(histogram_review_count, ensure_ascii=False)
        else:
            histogram_review_count = ''
        return histogram_review_count

    # BSR
    def get_reserve_2(self):
        all_rank_1 = self.sel.xpath('.//*[contains(text(), "Best Sellers Rank")]/../*[2]/span/span')
        all_rank_2 = self.sel.xpath('//li[@id="SalesRank"]') if self.sel.xpath('//li[@id="SalesRank"]') \
            else self.sel.xpath('//tr[@id="SalesRank"]/td[@class="value"]')
        if all_rank_1:
            all_rank_list = []
            for rk in all_rank_1:
                rank = rk.xpath('./text()')
                cat = rk.xpath('.//a/text()')
                if len(cat) == 1:
                    all_rank_list.append(rank[0].replace('#', '') + cat[0] + ')')
                else:
                    all_rank_list.append(rank[0].replace('#', '') + '>'.join(cat))
            all_rank_list = json.dumps(all_rank_list)
        elif all_rank_2:
            all_rank_list = []
            top_rank = all_rank_2[0].xpath('./text()')
            top_name = all_rank_2[0].xpath('./a/text()')
            if top_name and top_rank:
                all_rank_list.append(
                    ''.join([tr.strip() for tr in top_rank]).replace('#', '').replace(')', '') + top_name[0] + ')')
            category_rank = all_rank_2[0].xpath('./ul/li')
            if category_rank:
                for cr in category_rank:
                    category_rank_num = cr.xpath('./span[1]/text()')
                    category_rank_name = cr.xpath('./span[2]//a//text()')
                    all_rank_list.append(
                        category_rank_num[0].replace('#', '') + ' in ' + '>'.join(category_rank_name))
            all_rank_list = json.dumps(all_rank_list, ensure_ascii=False)
        else:
            all_rank_list = ''
        return all_rank_list

    # 技术细节
    def get_reserve_3(self):
        tech_detail = dict()
        tech_1 = self.sel.xpath('//table[@id="productDetails_techSpec_section_1"]//tr')
        tech_2 = self.sel.xpath('//div[@id="prodDetails"]//table')
        if tech_1:
            for tt in tech_1:
                k = tt.xpath('./th/text()')
                v = tt.xpath('./td/text()')
                if k and k:
                    tech_detail[k[0].strip()] = v[0].strip()
        elif tech_2:
            trs = tech_2[0].xpath('.//tr')
            for tr in trs:
                k = tr.xpath('./td[@class="label"]/text()')
                v = tr.xpath('./td[@class="value"]/text()')
                if k and v:
                    tech_detail[k[0].strip()] = v[0].strip()
        if tech_detail:
            tech_detail = json.dumps(tech_detail, ensure_ascii=False)
        else:
            tech_detail = ''
        return tech_detail

    # 配送方
    def get_reserve_4(self):
        reserve_field_4_1 = self.sel.xpath('.//*[@id="merchant-info"]//text()')
        reserve_field_4_2 = self.sel.xpath('//div[@id="sold-by"]//span/text()')
        if reserve_field_4_1:
            reserve_field_4 = reserve_field_4_1
        elif reserve_field_4_2:
            reserve_field_4 = reserve_field_4_2
        else:
            reserve_field_4 = ''
        reserve_field_4 = ' '.join([rf.strip().replace('\n', '') for rf in reserve_field_4]).replace(':', '')
        return reserve_field_4

    # BSR第一
    def get_reserve_5(self):
        reserve_field_5 = self.sel.xpath('//div[contains(@id, "zeitgeistBadge")]/div/a/@title')
        if reserve_field_5:
            reserve_field_5 = reserve_field_5[0]
        else:
            reserve_field_5 = ''
        return reserve_field_5

    # 跟卖和最低价
    def get_reserve_6_7(self):
        domain = SiteType[self.suffix]
        currency = domain['currency']
        sign = domain['sign']
        reserve_field_6_7_1 = self.sel.xpath('//div[contains(@id, "olp")]/div/span[1]//text()')
        reserve_field_6_7_2 = self.sel.xpath('//div[@id="mbc"]//h5[1]/span//text()')
        reserve_field_6_7 = reserve_field_6_7_1 if reserve_field_6_7_1 else reserve_field_6_7_2
        if reserve_field_6_7:
            reserve_field_6_7 = ''.join(reserve_field_6_7).replace(sign, '').replace(currency, '').replace(' ', '').replace(
                '\xa0', '')
            reserve_field_6_7 = re.findall(r'\d+\.?\d*,*\d*\.?\d*', reserve_field_6_7)
            if len(reserve_field_6_7) > 1:
                reserve_field_6 = reserve_field_6_7[0]
                reserve_field_7 = reserve_field_6_7[1]
                if currency == 'EUR':
                    reserve_field_7 = reserve_field_7.replace('.', '').replace(',', '.')
                else:
                    reserve_field_7 = reserve_field_7.replace(',', '')
            elif reserve_field_6_7:
                reserve_field_6 = reserve_field_6_7[0]
                reserve_field_7 = 0
            else:
                reserve_field_6 = 0
                reserve_field_7 = 0
        else:
            reserve_field_6 = 0
            reserve_field_7 = 0

        try:
            reserve_field_6 = int(reserve_field_6)
        except ValueError:
            print('get_reserve_field_6 raise exception')
            reserve_field_6 = 0
        try:
            reserve_field_7 = float(reserve_field_7)
        except ValueError:
            print('get_reserve_field_7 raise exception')
            reserve_field_7 = 0
        return reserve_field_6, reserve_field_7
