from django.http import HttpResponseForbidden
from shop.models import Buyer
from django.shortcuts import redirect
from django.contrib import messages
def cross_access_by_product(req,product):
    if product.seller != req.user.username:
        print("Unauthorized")
        return HttpResponseForbidden("401 - You are unauthorized to access this page.")
    

def cross_access_by_buyer(req):
    try:
        b=Buyer.objects.get(user=req.user)
        return True
    except Exception as e:
        return False