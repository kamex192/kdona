from django.db import models


class Rakuten_books(models.Model):
    name = models.TextField()
    url = models.TextField(unique=True)
    price = models.TextField()
    release_date = models.TextField()
    artist = models.TextField()
    director = models.TextField()
    related_works = models.TextField()
    selling_agency = models.TextField()
    distributor = models.TextField()
    number_of_disks = models.TextField()
    duration = models.TextField()
    bonus_video = models.TextField()
    manufacturer_part_number = models.TextField()
    jan_code = models.TextField()
    in_store_code = models.TextField()
    set_content = models.TextField()


class Yahoo(models.Model):
    search_name = models.TextField(unique=True)
    search_name_fix = models.TextField(unique=True)
    yahoo_shop = models.TextField()
    yahoo_name = models.TextField()
    url = models.TextField()
    yahoo_price = models.TextField()
    yahoo_stock = models.TextField()


class Gei(models.Model):
    name = models.TextField()
    url = models.TextField(unique=True)
    price = models.TextField()
    post_date = models.TextField()
    jan_code = models.TextField()
    recommended_word = models.TextField()


class Mono(models.Model):
    search_name = models.TextField(unique=True)
    search_name_fix = models.TextField(unique=True)
    name = models.TextField()
    url = models.TextField()
    shop = models.TextField()
    price = models.TextField()
    list_price = models.TextField()
    release_date = models.TextField()
    maker = models.TextField()
    jan_code = models.TextField()
    asin_code = models.TextField()


class Antlion(models.Model):
    search_name = models.TextField(unique=True)
    search_name_fix = models.TextField(unique=True)
    item_name = models.TextField()
    url = models.TextField()
    jan_code = models.TextField()
    isbn10_code = models.TextField()
    category = models.TextField()
    product_type = models.TextField()
    maker = models.TextField()
    distributor = models.TextField()
    manufacturer_part_number = models.TextField()
    model_name = models.TextField()
    color = models.TextField()
    size = models.TextField()
    release_date = models.TextField()
    asin_code = models.TextField()
    amazon_stock = models.TextField()
    amazon_price = models.TextField()
