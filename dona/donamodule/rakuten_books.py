from . import common
from . import antlion

from django.db import connection
from django.http import HttpResponse
from dona.models import Rakuten_books
from dona.models import Gei
from dona.models import Mono

import chromedriver_binary

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import threading
import time

import re
import math

import random


class GetRakuten_booksThread(threading.Thread):
    def run(self):
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))

        # ドライバ初期化
        driver = common.init_driver()

        # month_url_dict = get_month_url(driver)
        month_url_dict = {'2020年5月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-05-01', '2020年6月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-06-01', '2020年7月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-07-01',
                          '2020年8月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-08-01', '2020年9月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-09-01', '2020年10月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-10-01', '2020年11月': 'https://books.rakuten.co.jp/calendar/003/monthly/?tid=2020-11-01'}
        driver.close()
        time.sleep(3)

        print(month_url_dict)
        # for month_url in month_url_dict.values():
        #     thread = threading.Thread(
        #         target=get_items_info, args=([month_url]))
        #     thread.start()

        # rand_month_url = random.sample(list(month_url_dict.values()), 1)
        rand_month_url = random.sample(
            list(month_url_dict.values()), len(month_url_dict.values()))
        print(rand_month_url)
        for month_url in rand_month_url:
            thread = threading.Thread(
                target=get_items_info, args=([month_url]))
            thread.start()


def get_month_url(driver):
    print('get_month_url start')
    month_url_dict = {}

    # googleでサイト検索
    site = '楽天ブックス'
    common.move_toppage_from_google(driver, site)

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

    # ドライバ初期化
    driver = common.init_driver()

    items_info_dict = {}
    items_info_url_set = set()

    max_item = get_max_item(driver, month_url)
    print(max_item)
    max_page = math.ceil((int(max_item) / 30))
    print(max_page)

    page_list = list(range(int(max_page)))
    rand_page_list = random.sample(page_list, len(page_list))
    print(rand_page_list)

    for page in rand_page_list:
        print('page:' + str(page))
        month_url_page = month_url + '&p=' + str(page+1) + '#rclist'
        print(month_url_page)
        tmp_info_url_set = get_items_info_url_set(driver, month_url_page)
        items_info_url_set = items_info_url_set.union(tmp_info_url_set)

    all_item = Rakuten_books.objects.all()
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
    item_info = Rakuten_books()

    item_info.item_url = item_info_url

    selector = 'h1[itemprop="name"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        item_info.name = element.text

    selector = 'span[itemprop="price"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        item_info.price = element.text.replace(',', '').replace('円', '')

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
        print(item_info.name)
        name = ''
        pattern = '.*?】(.*)'
        result = re.match(pattern, item_info.name)
        if result is not None:
            name = result.group(1).replace('【', ' ').replace('】', ' ')
        print('name .*?】')
        print(name)
        if name == '':
            print('name (.*)')
            pattern = '(.*)'
            result = re.match(pattern, item_info.name)
            if result is not None:
                name = result.group(1)

        _, item_info.asin_code, item_info.asin_name, item_info.asin_price = antilion.chg_name_to_asin(driver,
                                                                                                      name)
        print('no name to asin code end')
        print(item_info.asin_code)
        print(item_info.asin_name)
        print(item_info.asin_price)
    else:
        print('yes jan code')
        print(item_info.jan_code)
        _, item_info.asin_code, item_info.asin_name, item_info.asin_price = antilion.chg_jancode_to_asin(driver,
                                                                                                         item_info.jan_code)
        print('yes jan to asin code')
        print(item_info.asin_code)
        print(item_info.asin_name)
        print(item_info.asin_price)
        if item_info.asin_code == '':
            name = ''
            pattern = '.*?】(.*)'
            result = re.match(pattern, item_info.name)
            if result is not None:
                name = result.group(1).replace('【', ' ').replace('】', ' ')
            print('name .*?】')
            print(name)
            if name == '':
                print('name (.*)')
                pattern = '(.*)'
                result = re.match(pattern, item_info.name)
                if result is not None:
                    name = result.group(1)

            _, item_info.asin_code, item_info.asin_name, item_info.asin_price = antilion.chg_name_to_asin(driver,
                                                                                                          name)

            print('yes name to asin code')
            print(item_info.asin_code)
            print(item_info.asin_name)
            print(item_info.asin_price)

    try:
        item_info.save()
        time.sleep(3)
    except Exception as e:
        print(e)

    print('get_item_info end')
    return 'get_item_info'


def output_csv():
    print('output_csv start')
    response = common.output_csv(
        'Rakuten_books', Rakuten_books._meta, Rakuten_books.objects.all())
    print('output_csv end')
    return response
