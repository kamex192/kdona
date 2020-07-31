# Generated by Django 3.0.8 on 2020-07-30 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Err',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200)),
                ('item_code', models.CharField(max_length=200)),
                ('err', models.CharField(max_length=200)),
                ('err_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200)),
                ('item_code', models.CharField(max_length=200)),
                ('item_price', models.CharField(max_length=200)),
                ('is_monitor', models.CharField(max_length=200)),
                ('buy_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
