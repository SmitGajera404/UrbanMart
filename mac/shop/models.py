from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.
class Product(models.Model):
    p_id=models.AutoField
    p_name=models.CharField(max_length=99)
    desc=models.CharField(max_length=1000)
    category=models.CharField(max_length=50,default="")
    subcategory=models.CharField(max_length=50,default="")
    price=models.IntegerField(default=0)
    p_date=models.DateField()
    p_plan=models.CharField(max_length=50,default="golden")
    stock=models.IntegerField(default=0)
    lifetime_sales=models.IntegerField(default=0)
    seller=models.CharField(max_length=100,default="")
    keywords=models.CharField(max_length=1000,default="")
    views=models.IntegerField(default=0)
    ratings=models.IntegerField(default=5)
    is_active=models.BooleanField(default=True)
    image=models.ImageField(upload_to="shop/images",default="")


    def __str__(self):
        return self.p_name+str(self.ratings)
class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=50)
    phone=models.CharField(max_length=10)
    subject=models.CharField(max_length=50)
    desc=models.CharField(max_length=500)

    def __str__(self):
        return self.name

class AddressLine(models.Model):
    id=models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=50)
    address=models.CharField(max_length=120)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    zip_code=models.CharField(max_length=10)
    phone=models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
class Orders(models.Model):
    id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=20000)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    payment_id = models.CharField(max_length=100,default="")
    address_line=models.ForeignKey(AddressLine,on_delete=models.CASCADE,null=True)
    sellers=models.CharField(max_length=2000,default="")
    timestamp=models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return self.user.username
    

class CanceledOrders(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class OrderUpdate(models.Model):
    id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default=0)
    update_desc=models.CharField(max_length=5000)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:10]+"..."
class Cart(models.Model):
    username=models.CharField(max_length=100,primary_key=True)
    cart_json=models.CharField(max_length=20000)

    def __str__(self):
        return self.username
class ProductReview(models.Model):
    sno=models.AutoField(primary_key=True)
    review=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    likes=models.IntegerField(default=0)
    dislikes=models.IntegerField(default=0)
    parent=models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    ratings=models.IntegerField(default=5)
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return self.user.username+" on "+self.product.p_name
class Buyer(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class UserLikes(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    liked=models.CharField(max_length=3000)
    disliked=models.CharField(max_length=3000)

    def __str__(self):
        return self.user.username
    
class Expert(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=1000)

    def __str__(self):
        return self.user.username

