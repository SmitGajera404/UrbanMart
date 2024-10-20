# shop/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'), 
    path('signin/',views.signin,name='signin'),
    path('sendotp/',views.sendotp,name='sendotp'),
    path('signinwithotp/',views.signinwithotp,name='signinwithotp'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('productview/<int:id>',views.productview,name='productview'),
    path('addproduct/',views.addproduct,name='addproduct'),
    path('checkOrders/',views.checkOrders,name='checkOrders'),
    path('like/',views.addLike,name='addlike'),
    path('dislike/',views.addDislike,name='addlike'),
    path('pendingInventoryTransfers/',views.pendingInventoryTransfers,name='pendingInventoryTransfers'),
    path('editProduct/<int:id>',views.editProduct,name='editProduct'),
    path('refillInventory/<int:id>',views.refillInventory,name='refillInventory'),
    path('get_bank_by_ifsc/',views.getBankByIFSC,name="get_bank_by_ifsc"),
    path('withdraw/',views.withdraw,name="withdraw"),
    path('discontinue/<int:id>',views.discontinue,name="discontinue"),


    # Dashboard APIs
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('plot_sales_data/', views.plot_sales_data, name='plot_sales_data'),
    path('plot_sales_order/', views.plot_sales_order, name='plot_sales_order'),
    path('top_5_best_sellers/', views.top_5_best_sellers, name='top_5_best_sellers'),
    path('revenue_contrib_category/', views.revenue_contrib_category, name='revenue_contrib_category'),
    path('view_to_order_funnel/', views.view_to_order_funnel, name='view_to_order_funnel'),
    path('order_volume_by_day/',views.order_volume_by_day,name="order_volume_by_day"),

    # Product Dashboard APIS
    path('product_dashboard/<int:id>', views.product_dashboard, name='product_dashboard'),
    path('plot_sales_trend/<int:id>', views.plot_sales_trend, name='plot_sales_trend'),
    path('order_volume/<int:id>', views.order_volume, name='order_volume'),
    path('sales_distribution/<int:id>', views.sales_distribution, name='sales_distribution'),
    path('word_freq/<int:id>', views.word_freq, name='word_freq'),
]
