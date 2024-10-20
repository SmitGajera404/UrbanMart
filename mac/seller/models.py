from django.db import models
from shop.models import Product
from django.contrib.auth.models import User

class DailySales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    sales = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.product.p_name} - {self.date} - {self.sales}'
    
class CategoricalRevenue(models.Model):
    category = models.CharField(max_length=500)
    revenue = models.IntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE)


class WithdrawRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50,default="")
    ifsc_code = models.CharField(max_length=50,default="")
    amount = models.IntegerField()
    status = models.CharField(max_length=100, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class CurrentBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username