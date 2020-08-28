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


class GetInfoThread(threading.Thread):
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
        for month_url in month_url_dict.values():
            get_items_info(driver, month_url)


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


def get_items_info(driver, month_url):
    print('get items info start')
    print(month_url)
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

    item_info_dict = {}
    item_info_dict['item_url'] = item_info_url
    item_info.item_url = item_info_url

    selector = 'h1[itemprop="name"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        item_info_dict['item_name'] = element.text
        item_info.item_name = element.text

    selector = 'span[itemprop="price"]'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        print(element.text)
        item_info_dict['item_price'] = element.text.replace(
            ',', '').replace('円', '')
        item_info.item_price = element.text.replace(',', '').replace('円', '')

    selector = 'li.productInfo'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if '発売日' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['release_date'] = result.group(1).replace(
                    '年', '-').replace('月', '-').replace('日', '')
                item_info.release_date = result.group(1).replace(
                    '年', '-').replace('月', '-').replace('日', '')
        if 'アーティスト' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['artist'] = result.group(1)
                item_info.artist = result.group(1)
        if '監督' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['director'] = result.group(1)
                item_info.director = result.group(1)
        if '関連作品' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['related_works'] = result.group(1)
                item_info.related_works = result.group(1)
        if '発売元' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['selling_agency'] = result.group(1)
                item_info.selling_agency = result.group(1)
        if '販売元' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['distributor'] = result.group(1)
                item_info.distributor = result.group(1)
        if 'ディスク枚数' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['number_of_disks'] = result.group(1)
                item_info.number_of_disks = result.group(1)
        if '収録時間' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['duration'] = result.group(1)
                item_info.duration = result.group(1)
        if '映像特典内容' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['bonus_video'] = result.group(1)
                item_info.bonus_video = result.group(1)
        if 'メーカー品番' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['manufacturer_part_number'] = result.group(1)
                item_info.manufacturer_part_number = result.group(1)
        if 'JANコード' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['jan_code'] = result.group(1)
                item_info.jan_code = result.group(1)
        if 'インストアコード' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['in_store_code'] = result.group(1)
                item_info.in_store_code = result.group(1)
        if 'セット内容' in element.text:
            print(element.text)
            pattern = '.*：  (.*)'
            result = re.match(pattern, element.text, flags=re.DOTALL)
            if result is not None:
                item_info_dict['set_content'] = result.group(1)
                item_info.set_content = result.group(1)

    try:
        item_info.save()
        time.sleep(3)
    except Exception as e:
        print(e)

    print('get_item_info end')
    return item_info_dict


class GetMonoThread(threading.Thread):
    def run(self):
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)

        all_item = Item.objects.exclude(jan_code__exact='')
        all_mono = Mono.objects.all()

        fetched_items_jan_code_set = set()
        print('all_item:'+str(len(all_item)))
        for item in all_item:
            fetched_items_jan_code_set.add(item.jan_code)

        fetched_monos_jan_code_set = set()
        print('all_mono:'+str(len(all_mono)))
        for mono in all_mono:
            fetched_monos_jan_code_set.add(mono.jan_code)

        fetch_jan_code_set = set()
        fetch_jan_code_set = fetched_items_jan_code_set.difference(
            fetched_monos_jan_code_set)

        print('diff_jan:'+str(len(fetch_jan_code_set)))
        for jan_code in fetch_jan_code_set:
            print(jan_code)
            get_mono_info(driver, jan_code)


def get_mono_info(driver, jan_code):
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

    time.sleep(random.randint(10,
                              15))
    # print(driver.page_source)
    try:
        selector = 'form.search_form input'
        element = driver.find_element_by_css_selector(selector)
        print(element.text)
        element.send_keys(jan_code)
        element.send_keys(Keys.ENTER)
        time.sleep(3)

        mono_info = Mono()
        mono_info.item_url = driver.current_url
        mono_info.jan_code = jan_code
        print(driver.current_url)
        print(jan_code)

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
        try:
            gei_info.save()
            print('gei_info.save')
            time.sleep(3)
        except Exception as e:
            print(e)


def index(request):
    content = r'hellow python, 123, end.'
    pattern = '.*lowp.*123.*'
    result = re.match(pattern, content)
    if result is not None:
        print('is not None')
    return HttpResponse('index')


def get_info(request):
    print('getinfo start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetInfoThread' not in str(threading.enumerate()):
        t = GetInfoThread()
        t.start()
    print('getinfo end')
    return HttpResponse('info')


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
