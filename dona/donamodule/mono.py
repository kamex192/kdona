from . import common
from dona.models import Mono
from dona.models import Gei

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
import random


class GetMonoThread(threading.Thread):
    def run(self):
        print('GetMonoThread start')
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))

        # ドライバ初期化
        driver = common.init_driver()

        # googleでサイト検索
        site = 'mnsearch'
        common.move_toppage_from_google(driver, site)

        # アイテム検索
        # search_name = '4549660409045'
        gei_obj = Gei.objects.all()
        gei_obj_rand = random.sample(list(gei_obj), len(gei_obj))
        for gei in gei_obj_rand:
            search_name = gei.name

            pattern = '.*?】(.*)'
            result = re.match(pattern, search_name, flags=re.DOTALL)
            if result is not None:
                search_name = result.group(1).replace(
                    '【', ' ').replace('】', ' ')

            print(search_name)
            search_item(driver, search_name)

        driver.close()
        print('GetMonoThread end')


def search_item(driver, search_name):
    print('search_item start')
    print(search_name)

    # time.sleep(random.randint(5, 10))

    wait = WebDriverWait(driver, 30)
    selector = 'form.search_form input'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    element.send_keys(search_name)
    element.send_keys(Keys.ENTER)

    url = driver.current_url
    print(url)

    selector = 'main'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))

    if '現在アクセスが集中' in element.text:
        print('現在アクセスが集中')
        site = 'mnsearch'
        common.move_toppage_from_google(driver, site)

        selector = 'form.search_form input'
        element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)))
        element.send_keys(search_name)
        element.send_keys(Keys.ENTER)

    mono = Mono()
    mono.search_name = search_name
    mono.url = driver.current_url

    if 'item?' in url:
        print('item')
        parse_mono_item(driver, mono)
    else:
        print('search')
        parse_mono_search(driver, mono)

    print('search_item end')


def parse_mono_item(driver, mono):
    print('parse_mono_item start')

    try:
        wait = WebDriverWait(driver, 30)
        selector = 'section#__main_content_title_area h3'
        name_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)))
        mono.name = name_element.text
    except Exception as e:
        print(e)
        return

    try:
        selector = 'table#_shopList_new tr'
        table_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))

        for table_element in table_elements:
            if table_element is None:
                break
            if 'サイト名' in table_element.text:
                print(table_element.text)
                continue
            print('table')
            selector = 'span.siteTitle'
            table_element_wait = WebDriverWait(table_element, 30)
            shop_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            mono.shop = shop_element.text

            selector = 'span.price'
            price_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            mono.price = price_element.text.replace(
                ',', '').replace('円', '')
            break
        try:
            print(vars(mono))
            mono.save()
            print('mono_info.save')
            time.sleep(3)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        return

    print('parse_mono_item end')


def parse_mono_search(driver, mono):
    print('parse_mono_search start')

    try:
        wait = WebDriverWait(driver, 30)
        selector = 'section.search_item_list_section'
        table_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for table_element in table_elements:
            selector = 'div.item_title_area a'
            table_element_wait = WebDriverWait(table_element, 30)
            url_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            print(url_element.get_attribute('href'))
            mono.url = url_element.get_attribute('href')

            selector = 'section._price_sale_date_wrapper div'
            table_element_wait = WebDriverWait(table_element, 30)
            list_price_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            # print(list_price_element.text)
            pattern = '[\s\S]*￥(.*)'
            result = re.match(pattern, list_price_element.text)
            if result is None:
                continue

            mono.list_price = re.sub("[^0-9]+", "", result.group(1))
            print(mono.list_price)

            selector = 'section._price_sale_date_wrapper div + div div'
            table_element_wait = WebDriverWait(table_element, 30)
            release_date_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            print(release_date_element.text)
            mono.release_date = release_date_element.text

            selector = 'div._maker_wrapper div'
            table_element_wait = WebDriverWait(table_element, 30)
            maker_element = table_element_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)))
            print(maker_element.text)
            mono.maker = maker_element.text

            break

    except Exception as e:
        print(e)
        return

    print(vars(mono))

    driver.get(mono.url)

    parse_mono_item(driver, mono)

    print('parse_mono_search end')


def output_csv():
    print('output_csv start')
    response = common.output_csv(
        'Mono', Mono._meta, Mono.objects.all())
    print('output_csv end')
    return response
