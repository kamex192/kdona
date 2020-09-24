from .donamodule import common
from .donamodule import antlion
from .donamodule import mono
from .donamodule import rakuten_books
from .donamodule import gei

from collections import namedtuple
from django.db import connection
from django.http import HttpResponse

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

import csv
import urllib


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    print(desc)
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def fetch_yahoo_price(driver, jan_code):
    print('fetch_yahoo_price start')
    print(jan_code)
    yahoo_shop = ''
    yahoo_name = ''
    yahoo_url = ''
    yahoo_price = ''
    yahoo_stock = ''
    yahoo_data_list = []

    # googleでサイト検索
    site = 'Yahoo!ショッピング'
    common.move_toppage_from_google(driver, site)

    time.sleep(random.randint(5, 10))
    wait = WebDriverWait(driver, 10)

    try:
        selector = 'input#ss_yschsp'
        element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)))
        element.send_keys(jan_code)
        element.send_keys(Keys.ENTER)
        print('keys enter')
    except Exception as e:
        print(e)

    time.sleep(random.randint(10, 15))

    print('check search result')

    try:
        selector = 'div#h1link'
        element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)))
        print(element.text)
        if '（0件）' in element.text:
            print(element.text)
            return yahoo_shop, yahoo_name, yahoo_url, yahoo_price, yahoo_stock
    except Exception as e:
        print(e)

    try:
        selector = 'span._14BqurpMMZHv span'
        element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)))
        if '在庫ありのみ' in element.text:
            print(element.text)
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            element.click()
    except Exception as e:
        print(e)

    time.sleep(random.randint(10, 15))

    try:
        selector = 'div#itmcond ul a'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            if '新品' in element.text:
                print(element.text)
                url = element.get_attribute('href')
                print(url)
                element.send_keys(Keys.ENTER)
                break

        time.sleep(random.randint(10, 15))

        selector = 'ul#sort li a'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            if '価格が安い順' in element.text:
                print(element.text)
                actions = ActionChains(driver)
                actions.move_to_element(element).perform()
                element.click()
                break

        time.sleep(random.randint(10, 15))

        selector = 'li#searchResults1 div ul li'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            print(element.text)
            try:
                textlist = element.text.splitlines()
                for text in textlist:
                    pattern = '(.*)円'
                    result = re.match(pattern, text)
                    if result is not None:
                        print(text)
                        yahoo_price = re.sub("[^0-9]+", "", result.group(1))
                        print('yahoo_price:' + yahoo_price)
                break
            except Exception as e:
                print(e)
            print('roop end')
    except Exception as e:
        print(e)

    selector = 'div#prcrange form div'
    prcrange_element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    print(prcrange_element.text)
    # selector = 'input.vnA2X4dIGdZJ'
    selector = 'div input + span + input'
    max_prc_element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    max_prc_element.send_keys(yahoo_price)
    max_prc_element.send_keys(Keys.ENTER)

    time.sleep(random.randint(10, 15))

    try:
        selector = 'li#searchResults1 div ul li'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            print(element.text)
            try:
                selector = 'div div p a'
                url_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, selector)))
                yahoo_url = url_element.get_attribute('href')
                print('yahoo_url:' + yahoo_url)

                selector = 'div div p a'
                name_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, selector)))
                yahoo_name = name_element.text
                print('yahoo_name:' + yahoo_name)

                selector = 'div div div a div p'
                shop_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, selector)))
                yahoo_shop = shop_element.text
                print('yahoo_shop:' + yahoo_shop)

                if '在庫切れ' in element.text:
                    yahoo_stock = '在庫切れ'

                textlist = element.text.splitlines()
                for text in textlist:
                    pattern = '(.*)円'
                    result = re.match(pattern, text)
                    if result is not None:
                        print(text)
                        yahoo_price = re.sub("[^0-9]+", "", result.group(1))
                        print('yahoo_price:' + yahoo_price)

                yahoo_data_list.append({
                    'yahoo_url': yahoo_url, 'yahoo_shop': yahoo_shop, 'yahoo_name': yahoo_name, 'yahoo_price': yahoo_price, 'yahoo_stock': yahoo_stock})

            except Exception as e:
                print(e)
        print('roop end')
    except Exception as e:
        print(e)

    for yahoo_data in yahoo_data_list:
        print(yahoo_data)

    yahoo_data_list_sorted = sorted(
        yahoo_data_list, key=lambda x: x['yahoo_price'])
    for yahoo_data in yahoo_data_list_sorted:
        print(yahoo_data)

    yahoo_shop = yahoo_data_list_sorted[0]['yahoo_shop']
    yahoo_name = yahoo_data_list_sorted[0]['yahoo_name']
    yahoo_url = yahoo_data_list_sorted[0]['yahoo_url']
    yahoo_price = yahoo_data_list_sorted[0]['yahoo_price']
    yahoo_stock = yahoo_data_list_sorted[0]['yahoo_stock']

    print('name asin')
    print(jan_code)
    print(yahoo_shop)
    print(yahoo_name)
    print(yahoo_url)
    print(yahoo_price)
    print(yahoo_stock)

    print('fetch_yahoo_price end')
    return yahoo_shop, yahoo_name, yahoo_url, yahoo_price, yahoo_stock


def index(request):
    # ドライバ初期化
    driver = common.init_driver()

    fetch_yahoo_price(driver, 'FINAL FANTASY XIV　マイスタークオリティ　フィギュア　＜オメガ＞')
    driver.close()
    return HttpResponse('index')


def get_rakuten_books(request):
    print('get_rakuten_books start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetRakuten_booksThread' not in str(threading.enumerate()):
        t = rakuten_books.GetRakuten_booksThread()
        t.start()
    print('get_rakuten_books end')
    return HttpResponse('rakuten_books')


def get_mono(request):
    print('get_mono start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetMonoThread' not in str(threading.enumerate()):
        t = mono.GetMonoThread()
        t.start()
    print('get_mono end')
    return HttpResponse('mono')


def get_antlion(request):
    print('get_antlion start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetAntlionThread' not in str(threading.enumerate()):
        t = antlion.GetAntlionThread()
        t.start()
    print('get_antlion end')
    return HttpResponse('antilion')


def get_gei(request):
    print('get_gei start')
    print('active_count:' + str(threading.active_count()))
    print('enumerate:' + str(threading.enumerate()))
    if 'GetGeiThread' not in str(threading.enumerate()):
        print('GetGeiThread start')
        t = gei.GetGeiThread()
        t.start()
    print('get_gei end')
    return HttpResponse('gei')


def dell_all_gei(request):
    Gei.objects.all().delete()
    return HttpResponse('dell_all_gei')


def output_rakuten_books(request):
    print('output_rakuten_books start')
    response = rakuten_books.output_csv()
    print('output_rakuten_books end')
    return response


def output_mono(request):
    print('output_mono start')
    response = mono.output_csv()
    print('output_mono end')
    return response


def output_antlion(request):
    print('output_antlion start')
    response = antlion.output_csv()
    print('output_antlion end')
    return response


def output_gei(request):
    print('output_gei start')
    response = gei.output_csv()
    print('output_gei end')
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
    #     "SELECT * FROM dona_Rakuten_books LEFT OUTER JOIN dona_Mono ON dona_Rakuten_books.jan_code=dona_Mono.jan_code")
    cursor.execute(
        "SELECT * FROM dona_Rakuten_books INNER JOIN dona_Mono ON dona_Rakuten_books.asin_code=dona_Mono.asin_code")
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
    #     "SELECT * FROM dona_Rakuten_books LEFT OUTER JOIN dona_Mono ON dona_Rakuten_books.jan_code=dona_Mono.jan_code LEFT OUTER JOIN dona_Gei ON dona_Mono.item_name Like '%' || dona_Rakuten_books.item_name || '%'")
    cursor.execute(
        "SELECT * FROM dona_Rakuten_books INNER JOIN dona_Mono ON dona_Rakuten_books.asin_code=dona_Mono.asin_code INNER JOIN dona_Gei ON dona_Rakuten_books.asin_code=dona_Gei.asin_code")
    output_item_mono_gei_object = cursor.fetchall()
    print('len(cursor)')
    print(len(output_item_mono_gei_object))

    for output_item_mono_gei in output_item_mono_gei_object:
        writer.writerow([*output_item_mono_gei])

    return response


def check(request):
    # ドライバ初期化
    driver = common.init_driver()

    # googleでサイト検索
    site = 'ブラウザ情報表示'
    common.move_toppage_from_google(driver, site)

    ret = '自動操縦フラグチェック：'

    selector = 'div.infArea'
    elements = driver.find_elements_by_css_selector(selector)
    for element in elements:
        if 'window.navigator.webdriver' in element.text:
            if 'true' in element.text:
                ret = ret + 'ばれてるよー ' + element.text
                print(ret)

    return HttpResponse(ret)
