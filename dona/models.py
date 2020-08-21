from django.db import models


class Item(models.Model):
    item_name = models.TextField()
    item_url = models.TextField(unique=True)
    item_price = models.TextField()
    release_date = models.DateTimeField()
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


class Err(models.Model):
    item_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=200)
    err = models.CharField(max_length=200)
    err_date = models.DateTimeField('date published')
