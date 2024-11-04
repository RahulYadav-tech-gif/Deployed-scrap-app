from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'phone_number', 'address']

# Sign Up Serializer
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'phone_number', 'address']

    def create(self, validated_data):
        user = User.objects.create_user(
          **validated_data
        )
        return user
    
# OTP verify Serializer
class OTPVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['email', 'otp_code']

    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=4)


# class UserApprovalSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ['username', 'email']

    
# Sign In Serializer
class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=20)
    

# Forgot Password Serializer
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)



# New Password Serializer
class NewPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=20)
    confirm_password = serializers.CharField(max_length=20, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()

    class Meta:
        model = User  
        fields = ['new_password', 'confirm_password']


# Scrap Product Serializer
class ScrapProductSerializer(serializers.ModelSerializer):
    productCategoryName = serializers.CharField(source='productCategory.category_name', read_only=True)

    class Meta:
        model = ScrapProduct
        fields = '__all__'  # Include all fields from ScrapProduct
        read_only_fields = ['seller', 'productIsAvailable']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['productCategoryName'] = instance.productCategory.category_name  
        return representation
    


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'

# Driver Serializer
class DriverSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='driver.email', required=True)
    class Meta:
        model = Driver
        fields = '__all__'

# Collection Serializer
class CollectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionDetail
        fields = '__all__'





# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'






class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'