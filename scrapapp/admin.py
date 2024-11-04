from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'is_verified', 'is_superuser']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'is_verified']

@admin.register(ScrapProduct)
class ScrapProductAdmin(admin.ModelAdmin):
    list_display = ['get_seller_name', 'get_seller_email', 'productName', 'productCategory', 'productPrice', 'productQuantity', 'productDateUploaded', 'productCondition', 'productIsAvailable']
    search_fields = ('productName', 'productDescription', 'productCategory__category_name', 'seller__first_name')

    def get_seller_name(self, obj):
        return f"{obj.seller.first_name} {obj.seller.last_name}" if obj.seller else "No Seller"

    def get_seller_email(self, obj):
        return f"{obj.seller.email}" if obj.seller else "No Seller"
    
    get_seller_name.short_description = 'Seller' 
    get_seller_email.short_description = 'Email' 


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['condition_name']


@admin.register(Driver)
class ScrapProductDriver(admin.ModelAdmin):
    list_display = ['get_driver_name', 'driver', 'vehicleType', 'licenseNumber', 'vehicleNumber', 'availability']
    search_fields = ['get_driver_name', 'driver', 'vehicleType', 'availability']


    def get_driver_name(self, obj):
        return f"{obj.driver.first_name} {obj.driver.last_name}" if obj.driver else "No driver"

    get_driver_name.short_description = 'Driver Name' 



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_at', 'is_read']
    search_fields = ['message', 'created_at', 'is_read']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'payment_id', 'signature', 'created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'status', 'created_at']


@admin.register(CollectionDetail)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['get_driver_name', 'get_driver_email', 'get_seller_name', 'get_seller_email', 'get_product_name', 'get_product_price', 'get_product_collection_date', 'is_collected']

    def get_driver_name(self, obj):
        return f"{obj.driver_name.driver.first_name} {obj.driver_name.driver.last_name}" if obj.driver_name else "No driver"

    get_driver_name.short_description = 'Driver Name'

    def get_driver_email(self, obj):
        return f"{obj.driver_name.driver.email}" if obj.driver_name else "No driver"
    
    get_driver_email.short_description = 'Driver Email'

    # Seller 
    def get_seller_name(self, obj):
        return f"{obj.seller_name.first_name} {obj.seller_name.last_name}" if obj.seller_name else "No seller"

    get_seller_name.short_description = 'Seller Name'

    def get_seller_email(self, obj):
        return f"{obj.seller_name.email}" if obj.seller_name else "No seller"
    
    get_seller_email.short_description = 'Seller Email'

    # Product
    def get_product_name(self, obj):
        return f"{obj.product_name.productName}" if obj.product_name else "No product"
    
    get_product_name.short_description = 'Product Name'

    def get_product_price(self, obj):
        return f"{obj.product_name.productPrice}" if obj.product_name else "No product"
    
    get_product_price.short_description = 'Product Price'

    def get_product_collection_date(self, obj):
        return f"{obj.arrival_date}" if obj.arrival_date else "No arrival date"
    
    get_product_collection_date.short_description = 'Product Collect Date'