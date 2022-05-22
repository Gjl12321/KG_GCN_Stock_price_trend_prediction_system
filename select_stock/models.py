from django.db import models
from stock.models import Stock
from django.contrib.auth.models import User


class SelectStock(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    class Meta:
        ordering = ['user']




