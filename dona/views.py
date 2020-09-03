from collections import namedtuple
from django.db import connection
from django.http import HttpResponse
from dona.models import Item
from dona.models import Gei
from dona.models import Mono

import chromedriver_binary

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import threading
import time

import re
import math

import random

import csv
import urllib


class GetItemThread(threading.Thread):
    def run(self):
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)

        month_url_dict = get_month_url(driver)
        # month_url_dict = {'2020年5月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-05-01', '2020年6月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-06-01', '2020年7月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-07-01',
        #                   '2020年8月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-08-01', '2020年9月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-09-01', '2020年10月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-10-01', '2020年11月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-11-01'}
        print(month_url_dict)
        # for month_url in month_url_dict.values():
        #     thread = threading.Thread(
        #         target=get_items_info, args=([month_url]))
        #     thread.start()

        rand_month_url = random.sample(list(month_url_dict.values()), 3)
        print(rand_month_url)
        for month_url in rand_month_url:
            thread = threading.Thread(
                target=get_items_info, args=([month_url]))
            thread.start()


def get_month_url(driver):
    print('get_month_url start')
    month_url_dict = {}
    driver.get('https://www.google.com')
    element = driver.find_element(By.CSS_SELECTOR, '[name="q"]')
    element.send_keys("楽天ブックス")
    element.send_keys(Keys.ENTER)

    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        if '楽天ブックス' in element.text:
            url = element.get_attribute('href')
            print(url)
            element.send_keys(Keys.ENTER)
            break

    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'DVD' in element.text:
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            break

    time.sleep(3)
    print('新作')
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        if '新作' in element.text:
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            element.click()
            break

    print('今月')
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if '今月' in element.text:
            url = element.get_attribute('href')
            print(url)
            element.send_keys(Keys.ENTER)
            break

    print('期間で絞り込む')
    selector = 'div.search-period__accordion'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if '期間で絞り込む' in element.text:
            print(element.text)
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            element.click()
            break

    print('月')
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        pattern = '.*年.*月.*'
        result = re.match(pattern, element.text)
        if result is not None:
            url = element.get_attribute('href')
            print(element.text)
            print(url)
            month_url_dict[element.text] = url

    print('get month url end')
    return month_url_dict


def get_items_info(month_url):
    print('get items info start')
    print(month_url)
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    items_info_dict = {}
    items_info_url_set = set()

    max_item = get_max_item(driver, month_url)
    print(max_item)
    max_page = math.ceil((int(max_item) / 30))
    print(max_page)

    for page in range(max_page):
        month_url_page = month_url + '&p=' + str(page+1) + '#rclist'
        print(month_url_page)
        tmp_info_url_set = get_items_info_url_set(driver, month_url_page)
        items_info_url_set = items_info_url_set.union(tmp_info_url_set)

    all_item = Item.objects.all()
    fetched_items_info_url_set = set()
    print('all_item:'+str(len(all_item)))

    for item in all_item:
        # print(item.item_url)
        fetched_items_info_url_set.add(item.item_url)

    print('items_info_url_set:'+str(len(items_info_url_set)))
    # print(items_info_url_set)
    print('fetched_items_info_url_set:'+str(len(fetched_items_info_url_set)))
    # print(fetched_items_info_url_set)

    items_info_url_set = items_info_url_set.difference(
        fetched_items_info_url_set)

    print('items_info_url_set:'+str(len(items_info_url_set)))
    # print(items_info_url_set)

    for item_info_url in items_info_url_set:
        get_item_info(driver, item_info_url)

    print('get items info end')
    return items_info_dict


def get_max_item(driver, month_url):
    print('get max item start')
    max_item = 0
    driver.get(month_url)
    time.sleep(random.randint(5, 10))

    selector = 'div.rb-control__display-number'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        pattern = '.*全 (\d+)件.*'
        result = re.match(pattern, element.text)
        if result is not None:
            print(result)
            max_item = result.group(1)
            print(max_item)

    print('get max item end')
    return max_item


def get_items_info_url_set(driver, page_url):
    print('get_items_info_url_set start')

    items_info_url_set = set()
    driver.get(page_url)
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        url = element.get_attribute('href')
        if '/rb' in url:
            items_info_url_set.add(url)

    print('get_items_info_url_set end')
    return items_info_url_set


def get_item_info(driver, item_info_url):
    print('get_item_info start')

    driver.get(item_info_url)
    item_info = Item()

    item_info.item_url = item_info_url

    selector = 'h1[itemprop="name"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        item_info.item_name = element.text

    selector = 'span[itemprop="price"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        item_info.item_price = element.text.replace(',', '').replace('円', '')

    selector = 'li.productInfo'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if '発売日' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.release_date = result.group(1).replace(
                    '年', '-').replace('月', '-').replace('日', '')
        if 'アーティスト' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.artist = result.group(1)
        if '監督' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.director = result.group(1)
        if '関連作品' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.related_works = result.group(1)
        if '発売元' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.selling_agency = result.group(1)
        if '販売元' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.distributor = result.group(1)
        if 'ディスク枚数' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.number_of_disks = result.group(1)
        if '収録時間' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.duration = result.group(1)
        if '映像特典内容' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.bonus_video = result.group(1)
        if 'メーカー品番' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.manufacturer_part_number = result.group(1)
        if 'JANコード' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.jan_code = result.group(1)
        if 'インストアコード' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.in_store_code = result.group(1)
        if 'セット内容' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info.set_content = result.group(1)

    if item_info.jan_code == '':
        print('no name to asin code stat')
        print(item_info.jan_code)
        print(item_info.item_name)
        item_name = ''
        pattern = '.*】(.*)'
        result = re.match(pattern, item_info.item_name)
        if result is not None:
            item_name = result.group(1)
        print('item_name .*】')
        print(item_name)
        if item_name == '':
            print('item_name (.*)')
            pattern = '(.*)'
            result = re.match(pattern, item_info.item_name)
            if result is not None:
                item_name = result.group(1)

        item_info.asin_code, item_info.asin_name = chg_name_to_asin(driver,
                                                                    item_name)
        print('no name to asin code end')
        print(item_info.asin_code)
        print(item_info.asin_name)
    else:
        print('yes jan code')
        print(item_info.jan_code)
        item_info.asin_code, item_info.asin_name = chg_jancode_to_asin(driver,
                                                                       item_info.jan_code)
        print('yes jan to asin code')
        print(item_info.asin_code)
        print(item_info.asin_name)
        if item_info.asin_code == '':
            item_name = ''
            pattern = '.*】(.*)'
            result = re.match(pattern, item_info.item_name)
            if result is not None:
                item_name = result.group(1)
            print('item_name .*】')
            print(item_name)
            if item_name == '':
                print('item_name (.*)')
                pattern = '(.*)'
                result = re.match(pattern, item_info.item_name)
                if result is not None:
                    item_name = result.group(1)

            item_info.asin_code, item_info.asin_name = chg_name_to_asin(driver,
                                                                        item_name)

            print('yes name to asin code')
            print(item_info.asin_code)
            print(item_info.asin_name)

    try:
        item_info.save()
        time.sleep(3)
    except Exception as e:
        print(e)

    print('get_item_info end')
    return 'get_item_info'


class GetMonoThread(threading.Thread):
    def run(self):
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)

        cursor = connection.cursor()
        cursor.execute("SELECT dona_Item.jan_code AS item_jan_code, dona_Item.asin_code AS item_asin_code, dona_Mono.jan_code AS mono_jan_code, dona_Mono.asin_code AS mono_asin_code FROM dona_Item LEFT OUTER JOIN dona_Mono ON dona_Item.asin_code=dona_Mono.asin_code")

        item_mono_object = namedtuplefetchall(cursor)
        print('len(cursor)')
        print(len(item_mono_object))

        for item_mono in item_mono_object:
            if item_mono.item_asin_code == '':
                # print('no asin code item_mono')
                # print(item_mono)
                continue
            if item_mono.mono_asin_code is None:
                # print('fetch mono data')
                print(item_mono)
                get_mono_info(driver, item_mono)


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    print(desc)
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def get_mono_info(driver, code):
    driver.get('https://www.google.com')
    element = driver.find_element(By.CSS_SELECTOR, '[name="q"]')
    element.send_keys("モノサーチ")
    element.send_keys(Keys.ENTER)

    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        url = element.get_attribute('href')
        if 'mnsearch' in str(url):
            print(url)
            element.send_keys(Keys.ENTER)
            break

    print('start sleep')
    time.sleep(random.randint(5, 10))
    print('end sleep')
    # print(driver.page_source)
    try:
        selector = 'form.search_form input'
        element = driver.find_element_by_css_selector(selector)
        print(element.text)
        element.send_keys(code.item_asin_code)
        element.send_keys(Keys.ENTER)
        time.sleep(3)

        mono_info = Mono()
        mono_info.item_url = driver.current_url
        mono_info.jan_code = code.item_jan_code
        mono_info.asin_code = code.item_asin_code
        print(mono_info.item_url)
        print(mono_info.jan_code)
        print(mono_info.asin_code)

        selector = 'section#__main_content_title_area h3'
    except Exception as e:
        print(e)
        return

    try:
        item_name_element = driver.find_element_by_css_selector(selector)
        mono_info.item_name = item_name_element.text
        print(item_name_element.text)
    except Exception as e:
        print(e)
        return

    try:
        selector = 'table#_shopList_new'
        shop_table_element = driver.find_element_by_css_selector(selector)

        selector = 'tr'
        shop_list_elements = shop_table_element.find_elements_by_css_selector(
            selector)

        for shop_list_element in shop_list_elements:
            if shop_list_element is None:
                break
            if 'サイト名' in shop_list_element.text:
                print(shop_list_element.text)
                continue
            print('table')
            selector = 'span.siteTitle'
            shop_name_element = shop_list_element.find_element_by_css_selector(
                selector)
            mono_info.shop_name = shop_name_element.text
            print(shop_name_element.text)

            selector = 'span.price'
            item_price_element = shop_list_element.find_element_by_css_selector(
                selector)
            mono_info.item_price = item_price_element.text.replace(
                ',', '').replace('円', '')
            print(item_price_element.text.replace(
                ',', '').replace('円', ''))

            break

        try:
            mono_info.save()
            print('mono_info.save')
            time.sleep(3)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
        return


class GetGeiThread(threading.Thread):
    def run(self):
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)

        url = 'http://blog.livedoor.jp/sedori_nitijyo/'
        get_gei_infos(driver, url)


def get_gei_infos(driver, url):
    print('get_gei_infos start')
    print(url)

    driver.get(url)

    max_page = get_max_gei_page(driver)
    print(max_page)

    for page in range(int(max_page)):
        url_page = url + '?p=' + str(page+1)
        print(url_page)
        get_gei_info(driver, url_page)

    print('get_gei_infos end')
    return 'get_gei_infos end'


def get_max_gei_page(driver):
    print('get_max_gei_page start')

    max_page = 0

    selector = 'li.paging-last a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        url = element.get_attribute('href')
        print(url)
        pattern = '.*?p=(\d+)'
        result = re.match(pattern, url)
        if result is not None:
            print(result)
            max_page = result.group(1)
            print(max_page)
        break

    print('get_max_gei_page end')
    return max_page


def get_gei_info(driver, url):
    print('get_gei_info start')
    print(url)

    driver.get(url)
    selector = 'div.article-outer'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        gei_info = Gei()
        selector = 'abbr.updated'
        post_date_element = element.find_element_by_css_selector(selector)
        gei_info.post_date = post_date_element.text.replace(
            '年', '-').replace('月', '-').replace('日', ' ')
        print(post_date_element.text)
        selector = 'div.article-title-outer'
        item_name_element = element.find_element_by_css_selector(selector)
        gei_info.item_name = item_name_element.text
        print(item_name_element.text)
        selector = 'h2 a'
        item_url_element = element.find_element_by_css_selector(selector)
        item_url = item_url_element.get_attribute('href')
        gei_info.item_url = item_url
        print(item_url)

        pattern = '.*】(.*)'
        result = re.match(pattern, gei_info.item_name, flags=re.DOTALL)
        if result is not None:
            gei_info.asin_code, gei_info.asin_name = chg_name_to_asin(driver,
                                                                      result.group(1))

        try:
            gei_info.save()
            print('gei_info.save')
            time.sleep(3)
        except Exception as e:
            print(e)


def chg_name_to_jan(driver, name):
    print('chg_name_to_jan start')
    jancode = ''
    asin_name = ''

    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # driver = webdriver.Chrome(options=options)

    url = 'https://antlion.xsrv.jp/'
    driver.get(url)
    print(url)
    time.sleep(random.randint(5, 10))
    selector = 'form#searchform input#s'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(name)
    element.send_keys(Keys.ENTER)
    time.sleep(random.randint(5, 10))

    try:
        selector = 'h4 a, li'
        elements = driver.find_elements_by_css_selector(selector)
        for element in elements:
            print(element.text)
            if element.get_attribute('href') is not None:
                print(element.text)
                asin_name = element.text
            print(element.text)
            if 'JAN' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    jancode = result.group(1)
                break
    except Exception as e:
        print(e)

    # driver.close()

    print('name jancode')
    print(name)
    print(jancode)
    print(asin_name)

    print('chg_name_to_jan end')
    return jancode, asin_name


def chg_name_to_asin(driver, name):
    print('chg_name_to_asin start')
    print(name)
    asin_code = ''
    asin_name = ''

    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # driver = webdriver.Chrome(options=options)

    url = 'https://antlion.xsrv.jp/'
    driver.get(url)
    print(url)
    time.sleep(random.randint(5, 10))
    selector = 'form#searchform input#s'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(name)
    element.send_keys(Keys.ENTER)
    time.sleep(random.randint(5, 10))
    try:
        selector = 'h4 a, li'
        elements = driver.find_elements_by_css_selector(selector)
        for element in elements:
            print(element.text)
            if element.get_attribute('href') is not None:
                print(element.text)
                asin_name = element.text
            if 'ASIN' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    asin_code = result.group(1)
                break
    except Exception as e:
        print(e)

    # driver.close()

    print('name asin')
    print(name)
    print(asin_code)
    print(asin_name)

    print('chg_name_to_asin end')
    return asin_code, asin_name


def chg_jancode_to_asin(driver, jancode):
    print('chg_jancode_to_asin start')
    asin_code = ''
    asin_name = ''

    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # driver = webdriver.Chrome(options=options)

    url = 'https://antlion.xsrv.jp/'
    driver.get(url)
    print(url)
    time.sleep(random.randint(5, 10))
    selector = 'form#searchform input#s'
    element = driver.find_element_by_css_selector(selector)
    element.send_keys(jancode)
    element.send_keys(Keys.ENTER)
    time.sleep(random.randint(5, 10))

    try:
        selector = 'h4 a, li'
        elements = driver.find_elements_by_css_selector(selector)
        for element in elements:
            print(element.text)
            if element.get_attribute('href') is not None:
                print(element.text)
                asin_name = element.text
            if 'ASIN' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    asin_code = result.group(1)
                break
    except Exception as e:
        print(e)

    # driver.close()

    print('jancode asin')
    print(jancode)
    print(asin_code)
    print(asin_name)

    print('chg_jancode_to_asin end')
    return asin_code, asin_name


def index(request):
    # chg_name_to_asin(
    #     '私の彼はエプロン男子')
    return HttpResponse('index')


def get_item(request):
    print('get_item start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetItemThread' not in str(threading.enumerate()):
        t = GetItemThread()
        t.start()
    print('get_item end')
    return HttpResponse('item')


def get_mono(request):
    print('get_mono start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetMonoThread' not in str(threading.enumerate()):
        t = GetMonoThread()
        t.start()
    print('get_mono end')
    return HttpResponse('mono')


def get_gei(request):
    print('get_gei start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetGeiThread' not in str(threading.enumerate()):
        t = GetGeiThread()
        t.start()
    print('get_gei end')
    return HttpResponse('gei')


def dell_all_gei(request):
    Gei.objects.all().delete()
    return HttpResponse('dell_all_gei')


def output_item(request):
    print('output_item start')
    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote((u'item.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    meta = Item._meta
    field_names = [field.name for field in meta.fields]
    for item in Item.objects.all():
        writer.writerow([getattr(item, field) for field in field_names])
    return response


def output_mono(request):
    print('output_mono start')
    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote((u'mono.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    meta = Mono._meta
    field_names = [field.name for field in meta.fields]
    for mono in Mono.objects.all():
        writer.writerow([getattr(mono, field) for field in field_names])
    return response


def output_gei(request):
    print('output_gei start')
    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote((u'gei.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    meta = Gei._meta
    field_names = [field.name for field in meta.fields]
    for gei in Gei.objects.all():
        writer.writerow([getattr(gei, field) for field in field_names])
    return response


def output_item_mono(request):
    print('output_item_mono start')
    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote((u'item_mono.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT * FROM dona_Item LEFT OUTER JOIN dona_Mono ON dona_Item.jan_code=dona_Mono.jan_code")
    cursor.execute(
        "SELECT * FROM dona_Item INNER JOIN dona_Mono ON dona_Item.asin_code=dona_Mono.asin_code")
    item_mono_object = cursor.fetchall()
    print('len(cursor)')
    print(len(item_mono_object))

    for item_mono in item_mono_object:
        writer.writerow([*item_mono])

    return response


def output_item_mono_gei(request):
    print('output_item_mono_gei start')
    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    filename = urllib.parse.quote((u'item_mono_gei.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        filename)
    writer = csv.writer(response)

    cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT * FROM dona_Item LEFT OUTER JOIN dona_Mono ON dona_Item.jan_code=dona_Mono.jan_code LEFT OUTER JOIN dona_Gei ON dona_Mono.item_name Like '%' || dona_Item.item_name || '%'")
    cursor.execute(
        "SELECT * FROM dona_Item INNER JOIN dona_Mono ON dona_Item.asin_code=dona_Mono.asin_code INNER JOIN dona_Gei ON dona_Item.asin_code=dona_Gei.asin_code")
    output_item_mono_gei_object = cursor.fetchall()
    print('len(cursor)')
    print(len(output_item_mono_gei_object))

    for output_item_mono_gei in output_item_mono_gei_object:
        writer.writerow([*output_item_mono_gei])

    return response


def check(request):
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com')
    # time.sleep(1)
    element = driver.find_element(By.CSS_SELECTOR, '[name="q"]')
    element.send_keys("ブラウザ情報 表示")
    # time.sleep(1)
    element.send_keys(Keys.ENTER)
    # time.sleep(1)
    selector = 'a'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'ブラウザ情報表示' in element.text:
            url = element.get_attribute('href')
            print(url)
            element.send_keys(Keys.ENTER)
            break

    time.sleep(10)

    ret = '自動操縦フラグチェック：'

    selector = 'div.infArea'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'window.navigator.webdriver' in element.text:
            if 'true' in element.text:
                ret = ret + 'ばれてるよー ' + element.text
                print(ret)

    return HttpResponse(ret)
