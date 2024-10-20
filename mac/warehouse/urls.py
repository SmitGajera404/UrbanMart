from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('pendingInventoryTransfers/',views.pendingInventoryTransfers,name='pendingInventoryTransfers'),
    path('checkOrders/',views.checkOrders,name='checkOrders'),
    path('updatestatus/<int:id>',views.updateStatus,name='updatestatus'),
    path('signin/',views.signin,name='signin'),
    path('productview/<int:id>',views.productview,name='productview'),
    path('logoutaccount/',views.logoutaccount,name='logoutaccount')
]