# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('track/', views.track, name='track'),
    path('productview/<int:id>', views.productview, name='productview'),
    path('checkout/', views.checkout, name='checkout'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart, name='cart'),
    path('cancel/<int:id>',views.cancel,name="cancel"),
    path('signin/',views.signin,name='signin'),
    path('orders/',views.displayOrders,name="orders"),
    path('sendotp/',views.sendotp,name='sendotp'),
    path('signinwithotp/',views.signinwithotp,name='signinwithotp'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('postReview/',views.postReview,name='postReview'),
    path('postReply/',views.postReply,name='postReply'),
    path('testing/',views.testing,name='testing'),
    path('like/',views.addLike,name='addlike'),
    path('dislike/',views.addDislike,name='addlike'),
    path('addlike/<int:id>/<str:no>',views.incereseLike,name='increaseLikes'),
    path('adddislike/<int:id>/<str:no>',views.incereseDislike,name='increaseLikes'),
     path('download-invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),
    path('testingForm/',views.testingForm,name='testingForm'),

    #payment APIS
    path('handlepayment/',views.handlepayment,name="handlepayment")
]
