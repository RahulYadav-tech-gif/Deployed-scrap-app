# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *

@receiver(post_save, sender=User)
def create_user_notification(sender, instance, created, **kwargs):
    if created:
        admin_user = User.objects.get(is_superuser=True)
        message = f"New User Signed up:\nFirst Name: {instance.first_name},\nLast Name: {instance.last_name},\nEmail: {instance.email},\nPhone Number: {instance.phone_number},\nAddress: {instance.address}"
        Notification.objects.create(user=admin_user, message=message)

@receiver(post_save, sender=ScrapProduct)
def create_product_notification(sender, instance, created, **kwargs):
    if created:
        admin_user = User.objects.get(is_superuser=True)
        message = (f"📦 New Product Added\n"
            f"Seller: {instance.seller.first_name}\n"
            f"Product Name: {instance.productName}\n"
            f"Category: {instance.productCategory}\n"
            f"Description: {instance.productDescription}\n"
            f"Price: {instance.productPrice}\n"
            f"Quantity: {instance.productQuantity}\n"
            f"Condition: {instance.productCondition}")
        Notification.objects.create(user=admin_user, message=message)


@receiver(post_save, sender=CollectionDetail)
def create_user_notification(sender, instance, created, **kwargs):
    if created:
        admin_user = User.objects.get(is_superuser=True)
        message = f"Driver assigned for product\n\nDriver Details:-\nFirst Name: {instance.driver_name.driver.first_name},\nLast Name: {instance.driver_name.driver.last_name},\nEmail: {instance.driver_name.driver.email},\nPhone Number: {instance.driver_name.driver.phone_number}\n\nProduct Details:- \nProduct Name: {instance.product_name.productName},\nProduct Category: {instance.product_name.productCategory},\nProduct Price: {instance.product_name.productPrice},\nProduct Quantity: {instance.product_name.productQuantity}"
        Notification.objects.create(user=admin_user, message=message)