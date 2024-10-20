from django.shortcuts import render,redirect
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponse
from django.contrib.auth import login,authenticate
from django.contrib.auth import logout as log_out
from shop.models import Product,Buyer,ProductReview,Orders,OrderUpdate,Expert,UserLikes
from warehouse.models import PendingInventoryTransfer
from .models import WithdrawRequest,CurrentBalance
import shop.emailEcomWEB as emailEcomWEB
from django.contrib import messages
from mac.decorators.login_required import login_required
from seller.middlewares import cross_access_middleware
from django.core.exceptions import ObjectDoesNotExist
from .Authentication import validateCredentials
import math,json,random,requests
from .dashboard_controller import dashboard_functions as dashboard_seller
from datetime import date


def discontinue(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.get(id=id)
    if product.stock == 0:
        product.is_active=False
        product.save()
    else:
        messages.error(req,"Product cannot be discontinued as it has stock")
        return redirect('/seller/')
    messages.success(req,"Product has been successfully unlisted!")
    return redirect('/seller/')



def getCurrentBalance(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')

    try:
        currentBalance = CurrentBalance.objects.get(user=req.user)
        return currentBalance.balance
    except:
        orders=Orders.objects.all()
        total_amount=0
        #{"user": {"seller1": [[2, 3]], "johndoe": [[3, 20]]}}
        for order in orders:
            sellers_info = json.loads(order.sellers)
            user_sellers = sellers_info.get('user', {})
            if req.user.username in user_sellers:
                referral_fees=0
                for item in user_sellers[req.user.username]:
                    product_id = item[1]
                    quantity = item[0]
                    product = Product.objects.get(id=product_id)
                    referral_fees=prod_plans[product.p_plan]*product.price*quantity
                    total_amount+=product.price*quantity-referral_fees
        return total_amount
            


def getBankByIFSC(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    ifsc = req.POST.get('ifsc')
    url = f"https://ifsc.razorpay.com/{ifsc}"
    response = requests.get(url)
    
    if response.status_code == 200:
        bank_details = response.json()
        return JsonResponse({'bank_name':bank_details['BANK'],'bank_branch':bank_details['BRANCH']},status=201)
    else:
        return JsonResponse({'error':" IFSC code not found."} , status=404)

@login_required
def withdraw(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method == 'POST':
        amount = req.POST.get('amount')
        bank_ifsc = req.POST.get('ifsc', '')
        bank_account_number = req.POST.get('account_number')

        sellerValidatedAmount = getCurrentBalance(req)
        if float(amount) > sellerValidatedAmount:
            return JsonResponse({'error': "Insufficient balance."}, status=404)

        if bank_ifsc:
            bank_details = json.loads(getBankByIFSC(req).content)
            try:
                if bank_details['bank_name']:
                    if bank_details['bank_branch']:
                        if len(bank_account_number) > 5 and int(bank_account_number):
                            #Database entry
                            withdrawRequest = WithdrawRequest(user=req.user,amount=int(amount),account_number=bank_account_number,ifsc_code=bank_ifsc.upper())
                            withdrawRequest.save()
                            try:
                                currentBalance = CurrentBalance.objects.get(user=req.user)
                                currentBalance.balance -= int(amount)
                                currentBalance.save()
                            except:
                                currentBalance = CurrentBalance(user=req.user,balance=sellerValidatedAmount-int(amount))
                                currentBalance.save()
                            return JsonResponse({'msg': 'validation successful'}, status=201)
            except KeyError:
                return JsonResponse({'error': "Invalid bank details."}, status=404)
            except ValueError:
                return JsonResponse({'error': "Invalid bank details."}, status=404)
        else:
            return JsonResponse({'error': "Invalid bank details."}, status=404)
    else:
        return JsonResponse({'error': "This page cannot be accessed directly."}, status=401)

def index(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    
    new_orders=0
    if req.user.is_authenticated:
        try:
            products=Product.objects.filter(seller=req.user.username)
            categories=Product.objects.filter(seller=req.user.username).values('category')
            no_of_orders = req.session.get('no_of_orders', 0)
            total_orders = Orders.objects.filter(sellers__contains='"'+req.user.username+'"').count()
            new_orders = total_orders - int(no_of_orders)
            print(total_orders,no_of_orders,new_orders)
        except ObjectDoesNotExist as e:
             params={"allprods":[],"count":0,"n":0}
             return render(req,'seller/index.html',params)
    else:
        products=Product.objects.all()
        categories=Product.objects.values('category')
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
    
    params={"allprods":allprods,"count":range(nslides),"n":nslides,"new_orders":new_orders,'balance':getCurrentBalance(req)}
    return render(req,'seller/index.html',params)
# Create your views here.


def signup(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method == 'POST':
        user_name = req.POST.get('name', '')
        email = req.POST.get('email', '')
        password = req.POST.get('password', '')
        users = User.objects.exclude(id__in=Buyer.objects.values('user'))
        for i in users:
            if i.email == email:
                messages.error(req,"Email is already associated with an account!")
                return redirect('/seller/')
        else:
           pass
        try:         
            myuser = User.objects.create_user(username=user_name, email=email, password=password)
            myuser.save()
            login(req,myuser,password)
            messages.success(req, "Your account has been successfully created")
            return redirect('/seller/')
        except IntegrityError as e:
            messages.warning(req, "Username already exists! please try again with different username")
            return redirect('/seller/')
        except Exception as e1:
            print(e1)
            messages.success(req, "Some error occured")
            return redirect('/seller/')
    return render('seller/index.html')  # Correct path to your template
def signin(req):

    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method == 'POST':
        user_name = req.POST.get('username', '')
        password = req.POST.get('password', '')
        user = authenticate(username=user_name, password=password)
        if user is not None:
            try:
                buyer = Buyer.objects.get(user=user)
                messages.error(req,'Authorization failed: You do not have access to the seller page.')
            except ObjectDoesNotExist:
                login(request=req, user=user)
                messages.success(req,'Successfully logged in!')
        else:
            messages.error(req,'Invalid Credentials!!')
    return redirect('/seller/')
@login_required
def logout(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method=='POST':
        log_out(req)
        messages.success(req,'Log out successful!')
    return redirect('/seller/')
@login_required
def productview(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.filter(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product.first())
    if middlewareResponse:
        return middlewareResponse
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
            if expert:
                reviewTempList.append('expert')
                reviewTempList.append(product.first().category)
            else:
                reviewTempList.append('not_expert')
            reviewDict.append(reviewTempList.copy())
            reviewTempList.clear()       
        except:
            reviewDict.append(["neutral",review])
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
    return render(req,'seller/product.html',{'product':product[0],'reviews':reviewDict,'replies':replyDict,'ratingsFullstar':ratingsFullstar,'ratingEmptystar':ratingsEmptystar,'count':reviews.count(),'restricted':restricted,'balance':getCurrentBalance(req)})
def sendotp(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method == 'POST':
        email = req.POST.get('email1', '')
        users = User.objects.exclude(id__in=Buyer.objects.values('user'))
        for i in users:
            if i.email == email:
                break
        else:
            return JsonResponse({'msg': 'Email not found!'})
        if email:
            otp = random.randint(100000, 999999)
            print('Generated OTP:', otp)

            try:
                emailEcomWEB.sendOtpMail(email, otp)
                print('OTP email sent to:', email)
                req.session['otp']=otp
                return JsonResponse({'msg': 'success','email':email})
            except Exception as e:
                print('Error sending OTP email:', str(e))
                return JsonResponse({'msg': 'error', 'error': str(e)})
        else:
            print('No email provided')
            return JsonResponse({'msg': 'no email'})
    return JsonResponse({'msg': 'invalid request'})
def signinwithotp(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method == 'POST':
        email=req.POST.get('hidden-email','')
        otpGet=req.POST.get('otp','')
        otp=req.session.get('otp',None)
        print('email: ',email,'otp from user: ',otpGet,'otp: ',otp)
        if(str(otp)==str(otpGet)):
            user=User.objects.filter(email=email).first()
            login(req,user)
            messages.success(req,'Successfully logged in!!')
            return JsonResponse({'msg':'success'},status=250)
        else:
            return JsonResponse({'msg': 'Invalid OTP!'},status=400)
    return redirect('/seller/')
@login_required
def addproduct(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    if req.method=='POST':
        p_name=req.POST.get('product-name','')
        price=req.POST.get('price','')
        desc=req.POST.get('description','')
        category=req.POST.get('category','')
        subcategory=req.POST.get('subcategory','')
        stock=req.POST.get('total-stock','')
        keywords=req.POST.get('search-keywords','')
        p_plan=req.POST.get('product-plan','')
        image=req.FILES.get('product-image','')
        if '' in [p_name,price,desc,category,subcategory,stock,keywords,p_plan,image]:
            messages.warning(req,"All fields are must required!")
            return render(req,'seller/addproduct.html',{'balance':getCurrentBalance(req)})
        if int(stock)<1:
            messages.error(req,'Stock should be greater than 0!!',{'balance':getCurrentBalance(req)})
            return render(req,'seller/addproduct.html')
        
        product = PendingInventoryTransfer(
        p_name=p_name,
        p_date=date.today(),
        price=price,
        desc=desc,
        p_plan=p_plan,
        category=category,
        subcategory=subcategory,
        stock=stock,
        keywords=keywords,
        image=image,
        seller=req.user.username
        )
        product.save()
        emailEcomWEB.sendInventoryTransferMail(req.user.email,req.user.username)
        messages.warning(req,"Your product will not be listed until you transfer your inventory. For further details, please check your email.")
    return render(req,'seller/addproduct.html',{'balance':getCurrentBalance(req)})
prod_plans={'platinum':0.20,'golden':0.13,'silver':0.07}
@login_required
def checkOrders(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    orders=Orders.objects.all()
    myProdArray=[]   
    myproducts={}
    #{"user": {"seller1": [[2, 3]], "johndoe": [[3, 20]]}}
    myProdArray = []
    for order in orders:
        sellers_info = json.loads(order.sellers)
        user_sellers = sellers_info.get('user', {})
        if req.user.username in user_sellers:
            myOrderUpdates={}
            orderUpdates=OrderUpdate.objects.filter(order_id=order.id)
            print(order.id)
            for orderUpdate in orderUpdates:
                orderUpdateMessage=orderUpdate.update_desc
                substrings = ['placed','shipped','packed','delivered']
                for i in substrings:
                    if i in orderUpdateMessage.lower():
                        myOrderUpdates[i]=[True,orderUpdate.timestamp]
                    else:
                        try:
                            if myOrderUpdates[i][0]:
                                pass
                        except Exception as e:
                            myOrderUpdates[i]=[False]
                if('out for delivery' in orderUpdateMessage.lower()):
                    myOrderUpdates['out_for_delivery']=[True,orderUpdate.timestamp]
                else:
                    myOrderUpdates['out_for_delivery']=[False]
            myproducts = {}
            referral_fees=0
            for item in user_sellers[req.user.username]:
                product_id = item[1]
                quantity = item[0]
                product = Product.objects.get(id=product_id)
                referral_fees=prod_plans[product.p_plan]*product.price*quantity
                myproducts[product] = [quantity,myOrderUpdates,prod_plans[product.p_plan]*100,referral_fees,product.price*quantity-referral_fees]    
                
                
            myProdArray.append(myproducts)
            print(myProdArray)
    req.session['no_of_orders'] = len(myProdArray)
    #[{<Product: Boat Airbuds 141>: 2, <Product: Raybun Sunglass (1 item)>: 1}]
            
    return render(req,'seller/checkorders.html',{'products':myProdArray,'balance':getCurrentBalance(req)})
@login_required
def pendingInventoryTransfers(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    inventoryTransfers=PendingInventoryTransfer.objects.filter(seller=req.user.username)
    return render(req,'seller/pending_inventory_transfers.html',{'products':inventoryTransfers,'balance':getCurrentBalance(req)})
@login_required
def editProduct(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if req.method=='POST':
        name = req.POST.get('name','')
        description = req.POST.get('description','')
        keywords = req.POST.get('keywords','')
        category = req.POST.get('category','')
        subcategory = req.POST.get('subcategory','')
        price = req.POST.get('price','')
        p_plan=req.POST.get('product-plan','')
        image = req.FILES.get('image')
        if image:
            product.image = image
        if name!='' and p_plan!='' and description!='' and keywords!='' and category!='' and subcategory!='' and price!='':
            product.p_name=name
            product.desc=description
            product.keywords=keywords
            product.category=category
            product.subcategory=subcategory
            product.price=price
            product.p_plan=p_plan
            product.save()
            messages.success(req,product.p_name+" has been edited successfully")
            return redirect('/seller/')
        else:
            messages.error(req,"Please fill all the fields")
    return render(req,'seller/editproduct.html',{'product':product,'balance':getCurrentBalance(req)})
@login_required
def refillInventory(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if req.method=='POST':
        stock = req.POST.get('stock','')
        emailEcomWEB.sendInventoryTransferOnRefillStockMail(req.user.email,req.user.email)
        if stock=='' or int(stock)<1:
            messages.error('Enter valid number')
        else:
            pendingInventoryTransfer=PendingInventoryTransfer(p_name=product.p_name,p_id=product.id,desc=product.desc,category=product.category,subcategory=product.subcategory,p_date=product.p_date,seller=product.seller,keywords=product.keywords,image=product.image,refill=True,stock=stock,price=product.price)
            pendingInventoryTransfer.save()
            messages.success(req,product.p_name+" has been added to pending inventory transfers")

    return render(req,'seller/refillstock.html',{'product':product,'balance':getCurrentBalance(req)})

@login_required
def plot_sales_data(request):
    cross_access_middleware.cross_access_by_buyer(request)
    return dashboard_seller.plot_sales_data(request)
@login_required
def revenue_contrib_category(request):
    cross_access_middleware.cross_access_by_buyer(request)
    return dashboard_seller.revenue_contrib_category(request)
@login_required
def view_to_order_funnel(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    return dashboard_seller.view_to_order_funnel(req)
@login_required
def order_volume_by_day(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    return dashboard_seller.order_volume_by_day(req)
@login_required
def plot_sales_order(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    return dashboard_seller.plot_sales_order(req)
@login_required
def top_5_best_sellers(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    return dashboard_seller.top_5_best_sellers(req)
@login_required
def seller_dashboard(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    return render(req, 'seller/seller_dashboard.html',{'balance':getCurrentBalance(req)})

@login_required
def product_dashboard(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if(product.p_plan == 'silver'):
        return HttpResponse("404 - Please Upgrade your product plan to Golden or Platinum to access this page")
    order_map = sales_distribution(req,id)
    return render(req,'seller/productdashboard.html', {'product':product,"map":order_map,'balance':getCurrentBalance(req)} )
@login_required
def plot_sales_trend(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')

    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if(product.p_plan == 'silver'):
        return HttpResponse("404 - Please Upgrade your product plan to Golden or Platinum to access this page")
    return dashboard_seller.plot_sales_trend(req,product)
@login_required
def order_volume(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')

    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if(product.p_plan == 'silver'):
        return HttpResponse("404 - Please Upgrade your product plan to Golden or Platinum to access this page")
    return dashboard_seller.order_volume(req,product)
@login_required
def sales_distribution(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')

    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if(product.p_plan == 'silver'):
        return HttpResponse("404 - Please Upgrade your product plan to Golden or Platinum to access this page")
    return dashboard_seller.sales_distribution(req,product)
@login_required
def word_freq(req,id):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
    product=Product.objects.get(id=id)
    middlewareResponse = cross_access_middleware.cross_access_by_product(req=req,product=product)
    if middlewareResponse:
        return middlewareResponse
    if(product.p_plan == 'silver'):
        return HttpResponse("404 - Please Upgrade your product plan to Golden or Platinum to access this page")
    return dashboard_seller.word_freq(req,product)



@login_required
def addLike(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
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
@login_required
def addDislike(req):
    buyerMiddlewareRes = cross_access_middleware.cross_access_by_buyer(req)
    if buyerMiddlewareRes:
        messages.warning(req,'You do not have access to that page')
        return redirect('/shop/')
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
