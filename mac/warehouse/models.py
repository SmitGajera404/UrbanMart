from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class PendingInventoryTransfer(models.Model):
    id=models.AutoField(primary_key=True)
    p_id=models.IntegerField(default=0)
    p_name=models.CharField(max_length=99)
    desc=models.CharField(max_length=1000)
    category=models.CharField(max_length=50,default="")
    subcategory=models.CharField(max_length=50,default="")
    price=models.IntegerField(default=0)
    p_plan=models.CharField(max_length=50,default="golden")
    p_date=models.DateField()
    stock=models.IntegerField(default=10)
    seller=models.CharField(max_length=100,default="")
    keywords=models.CharField(max_length=1000,default="")
    image=models.ImageField(upload_to="shop/images",default="")
    refill=models.BooleanField(default=False)

    def __str__(self):
        return self.p_name
    
class WarehouseUser(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username