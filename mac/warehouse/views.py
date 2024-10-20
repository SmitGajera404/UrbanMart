from django.shortcuts import render,redirect
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login,authenticate
from django.contrib.auth import logout as log_out
from shop.models import Product,Buyer,ProductReview,Orders,OrderUpdate
from warehouse.models import PendingInventoryTransfer
import shop.emailEcomWEB as emailEcomWEB
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from .Authentication import validateCredentials
from django.http import HttpResponse
import math,json,random
from .models import WarehouseUser
from datetime import date
# Create your views here.

def signin(req):
    if req.method == 'POST':
        user_name = req.POST.get('username', '')
        password = req.POST.get('password', '')
        user = authenticate(username=user_name, password=password)
        if user is not None:
            try:
                warehouseUser = WarehouseUser.objects.get(user=user)
                login(request=req, user=user)
                messages.success(req,'Successfully logged in!')
            except:
                return HttpResponse("401-You do not have access to this page")
        else:
            messages.error(req,'Invalid Credentials!!')
    return redirect('/warehouse/')

def logoutaccount(req):
    log_out(req)


def index(req):
    if not req.user.is_authenticated:
        return render(req,'warehouse/index.html',{'not_found':True})
    try:
        warehouseUser = WarehouseUser.objects.get(user=req.user)
    except:
        return HttpResponse("401-You do not have access to this page")

    new_orders=0
    if req.user.is_authenticated:
        try:
            products=Product.objects.all()
            categories=Product.objects.all().values('category')
            no_of_orders = req.session.get('no_of_orders', 0)
            total_orders = Orders.objects.all().count()
            new_orders = total_orders - int(no_of_orders)
            print(total_orders,no_of_orders,new_orders)
        except ObjectDoesNotExist as e:
             params={"allprods":[],"count":0,"n":0}
             return render(req,'seller/index.html',params)
    cat={item['category'] for item in categories}
    cat=list(cat)
    productTemp=[]
    allprods=[]
    nslides=0
    for i in cat:
        for j in products:
            if(j.category==i):
                productTemp.append(j)
        n=len(productTemp)
        nslides = n // 4 + math.ceil(n / 4 - (n // 4))
        allprods.append([productTemp.copy(),range(1,nslides),nslides])
        productTemp.clear()
    
    params={"allprods":allprods,"count":range(nslides),"n":nslides,"new_orders":new_orders}
    return render(req,'warehouse/index.html',params)
# Create your views here.


def pendingInventoryTransfers(req):
    if not req.user.is_authenticated:
        return render(req,'warehouse/index.html',{'not_found':True})

    try:
        warehouseUser = WarehouseUser.objects.get(user=req.user)
    except:
        return HttpResponse("401-You do not have access to this page")

    inventoryTransfers = PendingInventoryTransfer.objects.all()
    if req.method == 'POST':
        transfer_id = req.POST.get('filter',False)
        if transfer_id:
            inventoryTransfer = PendingInventoryTransfer.objects.filter(id=transfer_id)
            data = serialize('json', inventoryTransfer)
            return JsonResponse({'products': data}, safe=False)
        else:
            transfer_id=req.POST.get('transfer_id')
            inventoryTransfer = PendingInventoryTransfer.objects.filter(id=transfer_id).first()
            if inventoryTransfer.refill:
                product=Product.objects.get(id=inventoryTransfer.p_id)
                product.stock+=inventoryTransfer.stock
                product.save()
                inventoryTransfer.delete()
                messages.success(req,'Inventory refilled successfully!')
            else:
                product=Product(p_name=inventoryTransfer.p_name,p_plan=inventoryTransfer.p_plan,desc=inventoryTransfer.desc,category=inventoryTransfer.category,price=inventoryTransfer.price,p_date=inventoryTransfer.p_date,stock=inventoryTransfer.stock,seller=inventoryTransfer.seller,keywords=inventoryTransfer.keywords,image=inventoryTransfer.image)
                product.save()
                inventoryTransfer.delete()
                messages.success(req,'Product has been listed successfully')
    return render(req, 'warehouse/pending_inventory_transfers.html', {'products': inventoryTransfers})

def checkOrders(req):
    orders = Orders.objects.all()
    products={}
    productsObj=[]
    orderArray=[]
    
    for order in orders:    
        orderUpdates = OrderUpdate.objects.filter(order_id=order.id)
        action = 'no action'
        
        for i in orderUpdates:
            if 'packed' in i.update_desc:
                action = 'packed'
            elif 'at delivery station' in i.update_desc:
                action = 'at delivery station'
        if action!='at delivery station':
            orderArray.append([order, action])
            all_items=order.items_json
            items_dict = json.loads(all_items)
            for item,q in items_dict.items():
                product=Product.objects.get(id=item[2::])
                productsObj.append([q[0],product])
            products[order.id]=productsObj.copy()
            
            productsObj.clear()
    return render(req,'warehouse/orders.html',{'orders':orderArray,'products':products})

@login_required
def updateStatus(req,id):
    if req.method == 'POST':
        packed = req.POST.get('packed','')
        at_delivery_station = req.POST.get('at_delivery_station','')
        if packed != '':
            orderUpdate = OrderUpdate(order_id=id,update_desc='Your order has been packed')
            orderUpdate.save()
            messages.success(req,'Order has been updated successfully!')
        elif at_delivery_station != '':
            orderUpdate = OrderUpdate(order_id=id,update_desc='Your order has been at delivery station')
            orderUpdate.save()
            messages.success(req,'Order has been updated successfully!')
        else:
            messages.warning(req,'Please select an option')
            return redirect('checkOrders')
        return redirect('checkOrders')
        
        



@login_required
def productview(req,id):
    product=Product.objects.filter(id=id)
    reviews=ProductReview.objects.filter(product=product.first(),parent=None)
    ratingsFullstar=[]
    ratingsEmptystar=[]
    for review in reviews:
        ratingsFullstar.append(range(review.ratings))
        ratingsEmptystar.append(range(5-review.ratings))
    prod_user=product.first().seller
    restricted='Not restricted'
    if req.user.username==prod_user:
        restricted='restricted'
    return render(req,'warehouse/product.html',{'product':product[0],'ratingsFullstar':ratingsFullstar,'ratingEmptystar':ratingsEmptystar,'count':reviews.count(),'restricted':restricted})
