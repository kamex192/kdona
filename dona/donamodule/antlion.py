from . import common
from dona.models import Antlion

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
import datetime

import re
import math

import random


class GetAntlionThread(threading.Thread):
    def run(self):
        print('GetAntlionThread start')
        print('active_count:' + str(threading.active_count()))
        print('enumerate:' + str(threading.enumerate()))

        # ドライバ初期化
        driver = common.init_driver()

        # googleでサイト検索
        site = 'JANコード検索できる'
        common.move_toppage_from_google(driver, site)

        # アイテム検索
        search_name = '4549660409045'
        search_item(driver, search_name)

        driver.close()
        print('GetAntlionThread end')


def search_item(driver, search_name):
    print('search_item start')
    print(search_name)
    antlion = Antlion()
    antlion.search_name = search_name

    wait = WebDriverWait(driver, 30)
    selector = 'input#s'
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selector)))
    element.send_keys(search_name)
    element.send_keys(Keys.ENTER)

    try:
        print(driver.current_url)
        antlion.url = driver.current_url

        selector = 'article h4 a, article li, article div'
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, selector)))
        for element in elements:
            print(element.text)
            if 'JAN' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.jan_code = result.group(1)
            if element.get_attribute('href') is not None:
                print(element.text)
                antlion.item_name = element.text
            if 'ISBN-10コード' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.isbn10_code = result.group(1)
            if 'カテゴリ' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.category = result.group(1)
            if '商品種別' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.product_type = result.group(1)
            if 'メーカーブランド名' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.maker = result.group(1)
            if '発売元' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.distributor = result.group(1)
            if '発売元' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.distributor = result.group(1)
            if 'メーカー型番' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.manufacturer_part_number = result.group(1)
            if 'モデル名' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.model_name = result.group(1)
            if 'カラー' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.color = result.group(1)
            if 'サイズ' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.size = result.group(1)
            if '発売日' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.release_date = result.group(1)
            if 'ASIN' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.asin_code = result.group(1)
            if '在庫' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.amazon_stock = result.group(1)
            if 'Amazon販売価格' in element.text:
                print(element.text)
                pattern = '.* : (.*)'
                result = re.match(pattern, element.text, flags=re.DOTALL)
                if result is not None:
                    antlion.amazon_price = result.group(1).replace(
                        ',', '').replace('￥', '')
                    break
        if antlion.release_date is None:
            print('release_date is null')
            antlion.release_date = datetime.datetime.fromtimestamp(0)
    except Exception as e:
        print(e)

    try:
        antlion.save()
        time.sleep(3)
    except Exception as e:
        print(e)

    print('search_item end')


def output_csv():
    print('output_csv start')
    response = common.output_csv(
        'item', Antlion._meta, Antlion.objects.all())
    print('output_csv end')
    return response
