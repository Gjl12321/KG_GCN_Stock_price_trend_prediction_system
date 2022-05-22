from django.db import models
from django.contrib.auth.models import User


# 行业
class Industry(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='')
    code = models.CharField(max_length=30)


# 概念
class Concept(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default='')


# 热门概念
class HotConcept(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default='')


# 股东
class Holder(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='')


# 股票
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    stock_code = models.CharField(max_length=30)                    # 股票代码
    stock_name = models.CharField(max_length=100)                   # 股票名称
    stock_exchange = models.CharField(max_length=100)               # 股票交易所
    stock_company = models.CharField(max_length=100)                # 股票公司
    stock_start_date = models.DateTimeField()                       # 股票上市时间
    stock_industry = models.ForeignKey(Industry, on_delete=models.DO_NOTHING, null=True)
    stock_concept = models.ManyToManyField(Concept, null=True)
    stock_hot_concept = models.ManyToManyField(HotConcept, null=True)
    stock_place = models.CharField(max_length=50, null=True)        # 股票所属省市
    shenwan_1 = models.CharField(max_length=30, null=True)
    shenwan_2 = models.CharField(max_length=30, null=True)
    shenwan_3 = models.CharField(max_length=30, null=True)

    class Meta:
        ordering = ['stock_code']


