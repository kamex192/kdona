from django.db import models


class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=200)
    item_price = models.CharField(max_length=200)
    is_monitor = models.CharField(max_length=200)
    buy_date = models.DateTimeField('date published')


class Err(models.Model):
    item_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=200)
    err = models.CharField(max_length=200)
    err_date = models.DateTimeField('date published')
