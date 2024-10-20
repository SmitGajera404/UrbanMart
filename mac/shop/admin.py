from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ['p_name', 'ratings', 'seller', 'price']
class ExpertAdmin(admin.ModelAdmin):
    list_display = ['user', 'category']
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user','sno']

# Register the models separately
admin.site.register(Contact)
admin.site.register(CanceledOrders)
admin.site.register(Orders)
admin.site.register(AddressLine)
admin.site.register(OrderUpdate)
admin.site.register(Cart)
admin.site.register(Buyer)
admin.site.register(UserLikes)
admin.site.register(Expert,ExpertAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReview,ProductReviewAdmin)
