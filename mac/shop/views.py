import random,math,json,razorpay,os,re,datetime
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate,CanceledOrders,Cart,ProductReview,Buyer,AddressLine,UserLikes,Expert
from . import emailEcomWEB
from shop.payment import payment_controller
from seller.models import *
from .Authentication.validateCredentials import validateCredentials
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils.html import escapejs
from django.contrib import messages
from .templatetags import getdict
from django.contrib.auth import login,authenticate
import pandas as pd
from django.conf import settings
from django.contrib.auth import logout as log_out
from django.db.models import Case, When, IntegerField
custom_order = Case(
    When(p_plan='Platinum', then=1),
    When(p_plan='Golden', then=2),
    When(p_plan='Silver', then=3),
    output_field=IntegerField()
)
plan_pr={'platinum':0.20,'golden':0.13,'silver':0.07}
plan_order = {
        "platinum": 1,
        "golden": 2,
        "silver": 3
        }
def index(req):
    products=Product.objects.all()
    categories=Product.objects.values('category')
    cat={item['category'] for item in categories}
    cat=list(cat)
    productTemp=[]
    allprods=[]
    for i in cat:
        for j in products:
            if(j.category==i):
                productTemp.append(j)
        n=len(productTemp)
        nslides = n // 4 + math.ceil(n / 4 - (n // 4))
        productTemp.sort(key=lambda x: plan_order[x.p_plan.lower()])
        allprods.append([productTemp.copy(),range(1,nslides),nslides])
        productTemp.clear()
    params={"allprods":allprods,"count":range(nslides),"n":nslides}
    return render(req,'shop/index.html',params)

def checkLowStock(req,prod):
    totalSalesWeeks = (datetime.date.today() - prod.p_date).days//7
    if totalSalesWeeks==0:
        return False
    weekly_sales = prod.lifetime_sales/totalSalesWeeks
    threshold=(weekly_sales * 2)+(weekly_sales*0.1)
    print(threshold,prod.stock,totalSalesWeeks)
    if(prod.stock<=threshold):
        emailEcomWEB.sendLowStockEmail(req.user.email,prod.seller,prod,threshold)


@csrf_exempt
def handlepayment(req):
    return HttpResponse("Done")



@login_required
@csrf_exempt
def checkout(req):
    success=False
    o_id=0
    if req.method=='POST':
        payment_id = req.POST.get("payment_id",'')
        items_json = req.POST.get('cart','')
        name=req.POST.get('name','')
        email=req.POST.get('email','')
        address=req.POST.get('address','')
        city=req.POST.get('city','')
        state=req.POST.get('state','')
        zip_code=req.POST.get('zip_code','')
        phone=req.POST.get('phone','')
        prod_json=json.loads(items_json)
        userArray={'user':{}}

        payment_verification = payment_controller.verifyPaymentById(req,payment_id=payment_id)
        if not payment_verification:
            messages.warning(req,"Your payment is either not captured or payment is not done yet.")
            return redirect('/shop/')
        
        for i,j in prod_json.items():
            prod=Product.objects.get(id=int(i[2::]))
            userArray['user'][prod.seller]=[]
        for i,j in prod_json.items():
            prod=Product.objects.get(id=int(i[2::]))
            userArray['user'][prod.seller].append([j[0],prod.id])
        if name=='' and email=='':
            addr_id=req.POST.get('address_id')
            address_line=AddressLine.objects.get(id=int(addr_id))
            order=Orders(items_json=items_json,address_line=address_line,payment_id=payment_id,sellers=json.dumps(userArray),user=req.user)
        else:
            address_line=AddressLine(name=name,address=address,city=city,user=req.user,state=state,zip_code=zip_code,phone=phone,email=email)
            address_line.save()
            order=Orders(items_json=items_json,address_line=address_line,payment_id=payment_id,sellers=json.dumps(userArray),user=req.user)
        order.save()
        print("Hello")
        for i,j in prod_json.items():
            prod=Product.objects.get(id=int(i[2::]))
            prod.stock=prod.stock-j[0]
            if prod.stock == 0:
                emailEcomWEB.sendOutOfStockEmail(req,prod)
            try:
                categoricalRevenue = CategoricalRevenue.objects.get(category=prod.category,user=User.objects.get(username=prod.seller))
                categoricalRevenue.revenue += int(j[3])*j[0]-plan_pr[prod.p_plan]*int(j[3])*j[0]
                categoricalRevenue.save()
            except:
                categoricalRevenue = CategoricalRevenue(category=prod.category,revenue=int(j[3])*j[0]-plan_pr[prod.p_plan]*int(j[3])*j[0],user=User.objects.get(username=prod.seller))
                categoricalRevenue.save()
            try:
                dailySales = DailySales.objects.get(product=prod,date=datetime.date.today())
                dailySales.sales=dailySales.sales+j[0]
                dailySales.save()
            except:
                dailySales = DailySales(product = prod,sales=j[0],date=datetime.date.today())
                dailySales.save()
            prod.lifetime_sales+=j[0]
            checkLowStock(req,prod)
            prod.save()
        update=OrderUpdate(order_id=order.id,update_desc='The order has been placed.')
        update.save()
        o_id=order.id
        success=True
        emailEcomWEB.sendOrderPlacedMail(req,items_json,address_line.email,address_line.name,o_id)
    df=pd.read_csv('cities.csv')
    df=df[df['country_code'] == 'IN']
    columns_list = list(df['name'])
    c_list=list(set(list(df['state_name'])))
    address_lines=AddressLine.objects.filter(user=req.user)
    params={'order_id':o_id,'success':success,'api':columns_list,'api_state':c_list,'address_lines':address_lines}
    return render(req,'shop/checkout.html',params)
def about(req):
    return render(req,'shop/about.html')

def contact(req):
    if(req.method=="POST"):
        name=req.POST.get('name','')
        email=req.POST.get('email','')
        phone=req.POST.get('phone','')
        desc=req.POST.get('message','')
        subject=req.POST.get('subject','')
        contact=Contact(name=name,email=email,phone=phone,desc=desc,subject=subject)
        contact.save()
        emailEcomWEB.sendMailContactUs(name,email)
    return render(req,'shop/contact.html')
def track(req):
    if(req.method=="POST"):
        order_id=req.POST.get('orderid','')
        email=req.POST.get('email','')
        order=Orders.objects.filter(id=order_id,email=email)
        if(len(order)>0):
            update=OrderUpdate.objects.filter(order_id=order_id)
            updates=[]
            print('found')
            for item in update:
                updates.append({'text':item.update_desc,'time':str(item.timestamp)})
            return HttpResponse(json.dumps(updates))
        else:
            print('Not found')
            return HttpResponse(json.dumps([]))

    return render(req,'shop/tracker.html')
def productview(req,id):
    product=Product.objects.filter(id=id)
    reviews=ProductReview.objects.filter(product=product.first(),parent=None)
    reviewDict=[]
    for review in reviews:
        try:
            try:
                expert=Expert.objects.get(user=review.user,category=product.first().category)
            except:
                expert=None
            
            reviewTempList=[]
            user_like=UserLikes.objects.get(user=req.user)
            if '"'+str(review.sno)+'"' in user_like.liked:
                reviewTempList=["liked",review]
            elif '"'+str(review.sno)+'"' in user_like.disliked:
                reviewTempList=["disliked",review]
            else:
                reviewTempList=["neutral",review]
            if expert!=None:
                reviewTempList.append('expert')
                reviewTempList.append(product.first().category)
            else:
                reviewTempList.append('not_expert')
            reviewDict.append(reviewTempList.copy())
            reviewTempList.clear()       
        except:
            reviewDict.append(["neutral",review])
            if expert!=None:
                reviewDict[-1].append('expert')
                reviewDict[-1].append(product.first().category)
            else:
                reviewDict[-1].append('not_expert')
    replies=[]
    ratingsFullstar=[]
    ratingsEmptystar=[]
    for review in reviews:
        ratingsFullstar.append(range(review.ratings))
        ratingsEmptystar.append(range(5-review.ratings))
    allReplies=ProductReview.objects.all().exclude(parent=None)
    if req.user.username != product.first().seller:
        pg_views=product.first()
        pg_views.views+=1
        pg_views.save()
    
    for reply in allReplies:
        try:
            expert=Expert.objects.get(user=reply.user,category=product.first().category)
        except:
            expert=None
        if reply.user.username==reply.product.seller:
            replies.append([reply,'seller'])
        elif expert:
            replies.append([reply,'expert',product.first().category])
        else:
            replies.append([reply,'buyer'])
    replyDict={}
    for i in replies:
        if i[0].parent.sno not in replyDict.keys():
            replyDict[i[0].parent.sno]=[i]
        else:
            replyDict[i[0].parent.sno].append(i)
    prod_user=product.first().seller
    restricted='Not restricted'
    if req.user.username==prod_user:
        restricted='restricted'
    print(reviewDict)
    return render(req,'shop/product.html',{'product':product[0],'reviews':reviewDict,'replies':replyDict,'ratingsFullstar':ratingsFullstar,'ratingEmptystar':ratingsEmptystar,'count':reviews.count(),'restricted':restricted})
def search(req):
    if req.method=='POST':
        category=req.POST.get('category')
        subcategory=req.POST.get('subcategory')
        min_price=req.POST.get('min_price')
        max_price=req.POST.get('max_price')
        query=req.POST.get('query')
        sort_by=req.POST.get('sort-by')
        print("price",min_price,max_price)
        print("Phase 1")
        productsName = Product.objects.filter(p_name__icontains=query)
        productsDesc = Product.objects.filter(desc__icontains=query)
        productsKeywords=Product.objects.filter(keywords__icontains=query)
        print("Phase 2")
        productsQuery = productsKeywords.union(productsName).union(productsDesc)
        print("Phase 3")
        if category=='All':
            productsCategory = Product.objects.filter(category__icontains=query).union(Product.objects.filter(subcategory__icontains=query)).union(productsQuery)
        else:
            productsCategory = Product.objects.filter(category__icontains=category)
        if subcategory=='All':
            productsSubCategory = Product.objects.filter(subcategory__icontains=query).union(Product.objects.filter(category__icontains=query)).union(productsQuery)
        else:
            productsSubCategory = Product.objects.filter(subcategory__icontains=subcategory)
            
        if max_price=='':
            max_price=1000000
        if min_price=='':
            min_price=0
            print("Phase 4")     
        productsPrice=Product.objects.filter(price__lte=max_price,price__gte=min_price)
        print("Phase 5")
        products=productsCategory.intersection(productsSubCategory).intersection(productsPrice)
        for i in products:
            print(i)
        print("Phase 6",products)
        if sort_by=='price_high_low':
            products=products.order_by('-price')
        elif sort_by=='price_low_high':
            products=products.order_by('price')
        elif sort_by=='ratings_high_low':
            products=products.order_by('-ratings')
        elif sort_by=='ratings_low_high':
            products=products.order_by('ratings')
        else:
            products=products.order_by(custom_order)
        try:
            products=products.values('id', 'p_name', 'category', 'subcategory', 'price', 'desc','image','ratings','p_plan')
        except Exception as e:
            print(e,e.with_traceback)
        for i in products:
            print(i)
        print("Phase 7")
        params={'products':products,'query':query}
        print("Phase 8")
        
        return JsonResponse(list(products),safe=False)
    else:
        query=req.GET.get('query')
        query=query.lower()
        productsCategory = Product.objects.filter(category__icontains=query)
        productsSubCategory = Product.objects.filter(subcategory__icontains=query)
        productsName = Product.objects.filter(p_name__icontains=query)
        productsDesc = Product.objects.filter(desc__icontains=query)
        productsKeywords=Product.objects.filter(keywords__icontains=query)
        products = productsCategory.union(productsSubCategory).union(productsName).union(productsDesc).union(productsKeywords)
        allCats=products.values('category')
        allSubCats=products.values('subcategory')
        products=list(products)
        products.sort(key=lambda x: plan_order[x.p_plan.lower()])
        
        params={'products':products,'query':query,'allCats':allCats,'allSubCats':allSubCats}
        return render(req,'shop/search.html',  params)

def cart(req):
    cart = req.POST.get('cart', '{}')
    products = []
    quantity = []
    cartJSON = json.loads(cart)
    cj={}
    for i,j in cartJSON.items():
        cj[i]=j[0]
    for i, j in cj.items():
        products.append(Product.objects.filter(id=int(i[2::])))
        quantity.append(j)
    prods = zip(products, quantity)
    params = {'products': prods}
    return render(req, 'shop/cart.html', params)

def signup(req):
    if req.method == 'POST':
        user_name = req.POST.get('name', '')
        email = req.POST.get('email', '')
        password = req.POST.get('password', '')
        for i in User.objects.values('email'):
            if i['email'] == email:
                return JsonResponse({'msg': 'Email is already associated with an account'})
        try:
            validateCredentials(username=user_name,password=password,email=email)     
            myuser = User.objects.create_user(username=user_name, email=email, password=password)
            myuser.save()
            buyer=Buyer(user=myuser)
            buyer.save()
            return JsonResponse({'msg': 'User created successfully!'})
        except IntegrityError as e:
            print('unique')
            return JsonResponse({'msg': 'Username Already Exists!'})
        except Exception as e1:
            return JsonResponse({'msg' : str(e1)})
    return render(req,'shop/index.html')  # Correct path to your template
def signin(req):
    if req.method == 'POST':
        user_name = req.POST.get('username', '')
        password = req.POST.get('password', '')
        user = authenticate(username=user_name, password=password)
        if user is not None:
            login(request=req, user=user)
            cart = Cart.objects.filter(username=user_name).first()
            cart_json = json.loads(cart.cart_json) if cart else {}
            return JsonResponse({
                'cart': cart_json,  # Return the JSON directly without escaping
                'redirect_url': '/shop/'
            })
        else:
            messages.error(req,"Invalid credentials!")
            return JsonResponse({'error': 'Invalid Username or Password!!'}, status=400)
    return redirect('/shop/')
def logout(req):
    if req.method=='POST':
        user=req.user
        cartData=req.POST.get('cart')
        cart=Cart(username=user.username,cart_json=cartData)
        cart.save()
        log_out(req)
        messages.success(req,'Log out successful!')
    return redirect('/shop/')

def sendotp(req):
    if req.method == 'POST':
        email = req.POST.get('email1', '')
        for i in User.objects.values('email'):
            if i['email'] == email:
                break
        else:
            return JsonResponse({'msg': 'Email not found!'})
        if email:
            otp = random.randint(100000, 999999)
            try:
                emailEcomWEB.sendOtpMail(email, otp)
                req.session['otp']=otp
                return JsonResponse({'msg': 'success','email':email})
            except Exception as e:
                return JsonResponse({'msg': 'error', 'error': str(e)})
        else:
            print('No email provided')
            return JsonResponse({'msg': 'no email'})
    return JsonResponse({'msg': 'invalid request'})


def signinwithotp(req):
    if req.method == 'POST':
        email=req.POST.get('hidden-email','')
        otpGet=req.POST.get('otp','')
        otp=req.session.get('otp',None)
        print('email: ',email,'otp from user: ',otpGet,'otp: ',otp)
        if(str(otp)==str(otpGet)):
            user=User.objects.filter(email=email).first()
            cart = Cart.objects.filter(username=user.username).first()
            cart_json = json.loads(cart.cart_json) if cart else {}
            login(req,user)
            messages.success(req,'Successfully logged in!!')
            return JsonResponse({
                'cart': cart_json,
                'redirect_url': '/shop/'
            })
            
        else:
            print("Otp dismathched")
            return JsonResponse({'msg': 'Invalid OTP!'},status=400)
    return redirect('/shop/')
def postReview(req):
    if req.method=='POST':
        review=req.POST.get('review')
        user=req.user
        rating=req.POST.get('rating','')
        productId=req.POST.get('productId')
        try:
            product=Product.objects.filter(id=productId).first()
            product.ratings=(product.ratings+int(rating))//2
            product.save()
            prodReview=ProductReview(review=review,ratings=int(rating),product=product,user=user)
        except ValueError as e :
            messages.warning(req,'Select at least 1 star')
            return redirect('/shop/productview/'+productId)
        prodReview.save()
        try:
            try:
                expert=Expert.objects.get(user=req.user,category=product.category)
            except:
                allReviews=ProductReview.objects.filter(parent=None,user=req.user)
                allReviewsByCategory=[]
                for review in allReviews:
                    if review.product.category == product.category:
                        allReviewsByCategory.append(review)
                if len(allReviewsByCategory)>=3:
                    totalLikes=0
                    totalDislikes=0
                    for review in allReviewsByCategory:
                        totalLikes+=review.likes
                        totalDislikes+=review.dislikes
                    if totalLikes>4 and (totalLikes*0.4)>=totalDislikes:
                        Expert(user=req.user,category=product.category).save()
                        messages.success(req,f'Congratulations! You are now recognized as an expert in the {product.category} category.')
                        return redirect('/shop/productview/'+productId)
        except:
            pass
        messages.success(req,'Your review has been posted successfully')
        return redirect('/shop/productview/'+productId)
def incereseLike(req,id,no):
    review=ProductReview.objects.get(sno=id)
    review.likes+=int(no)
    review.save()
    return HttpResponse('Done')
def incereseDislike(req,id,no):
    review=ProductReview.objects.get(sno=id)
    review.dislikes+=int(no)
    review.save()
    return HttpResponse('Done')
def postReply(req):
    if req.method=='POST':
        reply=req.POST.get('reply')
        user=req.user
        productId=req.POST.get('productIdForReply')
        product=Product.objects.filter(id=productId).first()
        parent=ProductReview.objects.get(sno=req.POST.get('parent-sno'))
        prodReview=ProductReview(review=reply,product=product,user=user,parent=parent)
        prodReview.save()
        messages.success(req,'Your reply has been posted successfully')
    return redirect('/shop/productview/'+productId)
def testing(req):
    products=Product.objects.all()
    data={'data':[]}
    for product in products:
        data.get('data').append({'id':product.id,'image':product.image.name,
                     'name':product.p_name,'price':product.price,
                     'category':product.category})
    return JsonResponse(data)
import re
from django.http import JsonResponse

def testingForm(req):
    if req.method == 'GET':
        fname = req.GET.get('firstname', '').strip()
        lname = req.GET.get('lastname', '').strip()
        email = req.GET.get('email', '').strip()
        phone = req.GET.get('phone', '').strip()
        msg = req.GET.get('message', '').strip()

        errors = {}

        if not re.match('^[a-zA-Z]+$', fname):
            errors['firstname'] = 'First name should only contain alphabets'

        if not re.match('^[a-zA-Z]+$', lname):
            errors['lastname'] = 'Last name should only contain alphabets'

        if not re.match(r'^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})$', email):
            errors['email'] = 'Invalid email address'

        if not re.match('^[0-9]{10}$', phone):
            errors['phone'] = 'Invalid phone number'

        if not re.search('[a-zA-Z]', msg):
            errors['message'] = 'Message should contain at least one alphabet'

        if errors:
            return JsonResponse({'errors': errors})
        else:
            return JsonResponse({'success': 'All data is valid'})

    return JsonResponse({'404': 'Invalid request method'})
from django.http import FileResponse

def download_invoice(request, order_id):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f"invoice_{order_id}.pdf")
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

def addLike(req):
    if req.method=='POST':
        sno=req.POST.get('sno')
        
        try:
            user_like = UserLikes.objects.get(user=req.user)
            liked_reviews = json.loads(user_like.liked)
            disliked_reviews = json.loads(user_like.disliked)
            if sno not in liked_reviews:
                liked_reviews.append(sno)
                review=ProductReview.objects.get(sno=int(sno))
                review.likes+=1
                review.save()
                try:
                    disliked_reviews.remove(sno)
                    review=ProductReview.objects.get(sno=int(sno))
                    review.dislikes-=1
                    review.save()
                except :
                    pass
                user_like.liked = json.dumps(liked_reviews)
                user_like.disliked = json.dumps(disliked_reviews)
                user_like.save()
                data=["liked"]
                return JsonResponse(data, safe=False)
            else:
                data=["not liked"]
                return JsonResponse(data, safe=False)
        except UserLikes.DoesNotExist:
            
            user_like = UserLikes(
                user=req.user,
                liked=json.dumps([sno]),
                disliked=json.dumps([])
            )
            user_like.save()
            data=['new User']
            return JsonResponse(data,safe=False)
    
def addDislike(req):
    if req.method=='POST':
        sno=req.POST.get('sno')
        try:
            user_dislike = UserLikes.objects.get(user=req.user)
            disliked_reviews = json.loads(user_dislike.disliked)
            liked_reviews = json.loads(user_dislike.liked)
            if sno not in disliked_reviews:
                review=ProductReview.objects.get(sno=int(sno))
                review.dislikes+=1
                review.save()
                try:
                    liked_reviews.remove(sno)
                    review=ProductReview.objects.get(sno=int(sno))
                    review.likes-=1
                    review.save()
                except :
                    pass
                disliked_reviews.append(sno)
                user_dislike.liked = json.dumps(liked_reviews)
                user_dislike.disliked = json.dumps(disliked_reviews)
                user_dislike.save()
                data=["disliked"]
                return JsonResponse(data, safe=False)
            else:
                data=["not disliked"]
                return JsonResponse(data, safe=False)
        except UserLikes.DoesNotExist:
            user_dislike = UserLikes(
                user=req.user,
                liked=json.dumps([]),
                disliked=json.dumps([sno])
            )
            user_dislike.save()
            print("as dislike new",user_dislike)
    data=[1,3,4,5]
    return JsonResponse(data, safe=False)

def displayOrders(req):
    orders=Orders.objects.filter(user=req.user)
    orderArray=[]
    products={}
    productsObj=[]
    for order in orders:
        orderArray.append([order,OrderUpdate.objects.filter(order_id=order.id).order_by('timestamp'),OrderUpdate.objects.get(order_id=order.id,update_desc__icontains="placed")])
        all_items=order.items_json
        items_dict = json.loads(all_items)
        for item,q in items_dict.items():
            product=Product.objects.get(id=item[2::])
            productsObj.append([q[0],product])
        products[order.id]=productsObj.copy()
        productsObj.clear()
    
    return render(req,'shop/orderdisplay.html',{'orders':orderArray,'products':products})


def cancel(req,id):
    try:
        orderUpdate = OrderUpdate.objects.get(order_id=id,update_desc__icontains="packed")
        messages.info(req,'Order has been packed you cannot cancel your order now!')
        return redirect('/shop/orders/')
    except Exception as e:
        order=Orders.objects.get(id=id)
        all_items=order.items_json
        items_dict = json.loads(all_items)
        for item,q in items_dict.items():
            product=Product.objects.get(id=item[2::])
            product.stock+=q[0]
            product.lifetime_sales-=q[0]
            product.save()
        canceledOrder = CanceledOrders(user=req.user,payment_id=order.payment_id)
        canceledOrder.save()
        order.delete()
        messages.success(req,"Order has been canceled successfully!")
        return redirect('/shop/orders/')