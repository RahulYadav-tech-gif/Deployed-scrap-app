from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import random
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.text import slugify
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#User
class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, address=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, address=address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number=None, address=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(email, phone_number, address, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def generate_otp(self):
        self.otp_code = str(random.randint(1000, 9999))
        self.save()

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300
    

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Select_Category', 'Select Category'),
        ('Phone', 'Phone'),
        ('Cloth', 'Cloth'),
        ('Shoes', 'Shoes'),
        ('Accessories', 'Accessories'),
        ('Beauty', 'Beauty'),
        ('Furniture', 'Furniture'),
        ('Travel', 'Travel'),
        ('Sports', 'Sports'),
        ('Toy', 'Toy'),
        ('Gadgets', 'Gadgets'),
        ('Laptop', 'Laptop'),
        ('Other', 'Other')
    ]
    category_name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Select_Category')
   

    def __str__(self):
        return self.category_name
    
    
class Condition(models.Model):
    CONDITION_CHOICES = [
        ('Select Condition', 'Select Condition'),
        ('Used - Like New', 'Used - Like New'),
        ('Used - Very Good', 'Used - Very Good'),
        ('Used - Good', 'Used - Good'),
        ('Used - Acceptable', 'Used - Acceptable'),
    ]
    condition_name = models.CharField(max_length=100, choices=CONDITION_CHOICES, default='Select Condition')

    def __str__(self):
        return self.condition_name
    


class ScrapProduct(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    productName = models.CharField(max_length=100, blank=False)
    productCategory = models.ForeignKey(Category, on_delete=models.CASCADE,blank=True,null=True)
    productDescription = models.TextField()
    productImage = models.ImageField(upload_to='product_images/', blank=False)
    productPrice = models.IntegerField(blank=False)
    productQuantity = models.IntegerField(default=1)
    productDateUploaded = models.DateField(auto_now_add=True)
    productIsAvailable = models.BooleanField(default=True, blank=False)
    productCondition = models.ForeignKey(Condition, on_delete=models.CASCADE,blank=True,null=True)
    
    class Meta:
        ordering = ['-productDateUploaded']

class Driver(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicleType = models.CharField(max_length=100)
    licenseNumber = models.CharField(max_length=100, unique=True)
    vehicleNumber = models.CharField(max_length=100, unique=True)
    availability = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)


class CollectionDetail(models.Model):
    driver_name = models.ForeignKey(Driver, on_delete=models.CASCADE)
    seller_name = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    product_name = models.ForeignKey(ScrapProduct, on_delete=models.CASCADE)
    arrival_date = models.DateField(default=timezone.now)
    is_collected = models.BooleanField(default=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ScrapProduct, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField()


class Payment(models.Model):
    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class AdminTable(models.Model):
    pass

