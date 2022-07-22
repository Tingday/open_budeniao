from django.db import models


class user(models.Model):
    openid = models.CharField(max_length=32, primary_key=True)
    alipay = models.CharField(max_length=32)
    orders = models.IntegerField()
