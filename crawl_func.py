import random
import asyncio
from threading import Thread
import aiohttp
from aiohttp.client_exceptions import ClientError
from lxml import etree
from settings import HEADERS
from parse_html import choose_parse
from get_proxy_ip import update_proxy_ip


def start_thread(new_loop):
    thread = Thread(target=start_loop, args=(new_loop,))
    thread.setDaemon(True)
    thread.start()


def start_loop(loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except:
        print('start_loop exc')


def start_crawl(rds, que, conf, new_loop):
    if que.qsize() < conf.REMAIN:
        update_proxy_ip(que)

    if rds.count_members(conf.REDIS_CRAWL_URLS) < conf.CONCURRENT:
        item = rds.rds.lpop(conf.REDIS_START_URLS)
        if item:
            if isinstance(item, bytes):
                item = item.decode('utf-8')
            rds.add_set(conf.REDIS_REQUEST_URLS, item)

    item = rds.pop_member(conf.REDIS_REQUEST_URLS)
    if item:
        if isinstance(item, bytes):
            item = item.decode('utf-8')
        rds.add_set(conf.REDIS_CRAWL_URLS, item)
        asyncio.run_coroutine_threadsafe(req_http(que, rds, conf, item), new_loop)


async def req_http(que, rds, conf, mp):
    mapping = eval(mp)
    headers = {'User-Agent': random.choice(HEADERS)}
    proxy_ip = que.get()
    ip = proxy_ip['ip']
    proxy = 'http://{}'.format(ip)
    url = mapping['page_url']
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, proxy=proxy, timeout=conf.TIMEOUT) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    if exist_captcha(html):
                        print('captcha')
                        proxy_ip['num'] -= 1
                        rds.add_set(conf.REDIS_REQUEST_URLS, mp)
                    else:
                        print(url)
                        choose_parse(rds, conf, mp, html)
                elif resp.status == 404:
                    print('404')
                    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
                else:
                    proxy_ip['num'] -= 1
                    print(resp.status)
                    rds.add_set(conf.REDIS_REQUEST_URLS, mp)
    except ClientError:
        print('ClientError')
        proxy_ip['num'] -= 1
        rds.add_set(conf.REDIS_REQUEST_URLS, mp)
    except asyncio.TimeoutError:
        print('Timeout')
        proxy_ip['num'] -= 1
        rds.add_set(conf.REDIS_REQUEST_URLS, mp)
    except Exception as exp:
        proxy_ip['num'] -= 1
        print('Raise Exception: {!r}'.format(exp))
        rds.add_set(conf.REDIS_REQUEST_URLS, mp)
    finally:
        if proxy_ip['num'] > 0:
            que.put(proxy_ip)


def exist_captcha(html):
    sel = etree.HTML(html)
    captcha = sel.xpath('//input[@id="captchacharacters"]')
    if captcha:
        return True
    return False


def clear_rds(rds, conf):
    members = rds.get_all_members(conf.REDIS_REQUEST_URLS) | rds.get_all_members(conf.REDIS_CRAWL_URLS)
    for member in members:
        rds.rds.lpush(conf.REDIS_START_URLS, member)
    rds.delete_key(conf.REDIS_REQUEST_URLS)
    rds.delete_key(conf.REDIS_CRAWL_URLS)



