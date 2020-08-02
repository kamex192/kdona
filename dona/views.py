from django.http import HttpResponse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_binary

def get_fx_rate():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://info.finance.yahoo.co.jp/fx/')
    usd_jpy = driver.find_element(By.ID, 'USDJPY_top_bid').text
    driver.quit()
    return usd_jpy

def index(request):
    fx_rate = get_fx_rate()
    return HttpResponse(fx_rate)