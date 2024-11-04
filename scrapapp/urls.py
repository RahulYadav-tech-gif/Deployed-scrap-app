from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ScrapProductView, basename='scrapproduct')  # Product
router.register(r'drivers', DriverViewSet)                               # Driver
router.register(r'categories', CategoryViewSet)                          # Category
router.register(r'conditions', ConditionViewSet)                         # Condition
# router.register(r'collections', CollectionView)



urlpatterns = [
    # all detail view
    path('details/', AllDetailView.as_view(), name='all-details'),


    # Signup
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify_otp/', OTPVerifyView.as_view(), name='verify_otp'),
    

    # path('user_approval/<int:user_id>/', UserApprovalView.as_view(), name='user_approval'),


    # Signin
    path('signin/', SigninView.as_view(), name='sign-in'),


    # Forgot Password
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset_password_verify_otp/<int:id>/', ResetPasswordOTPVerifyView.as_view(), name='reset-password-verify-otp'),
    path('reset_password_view/<int:id>/', ResetPasswordView.as_view(), name="reset-password-view"),


    # CRUD operation in Scrap Product
    path('', include(router.urls)),
    # GET  /products/
    # POST  /products/
    # GET  /products/<id>/
    # PUT  /products/<id>/
    # DELETE  /products/<id>/


    # Category api
    path('', include(router.urls)), 


    # Condition api
    path('', include(router.urls)), 



    # Driver api
    path('', include(router.urls)), 
    # GET  /drivers/
    # POST  /drivers/
    # GET  /drivers/<id>/
    # PUT  /drivers/<id>/
    # DELETE  /drivers/<id>/
    # GET /drivers/available/
    # POST /drivers/assign_driver/

    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('payment/', Payment.as_view(), name='payment'),
    path('verify-payment/', PaymentVerificationView.as_view(), name='verify-payment'),

    # path('', include(router.urls)),

    path('inform-seller/', InformSeller.as_view(), name='inform-seller'),

    path('driver-seller-otp/', DriverSellerOTPView.as_view(), name='driver-seller-otp'),

    path('driver-seller-otp-verify/', DriverSellerOTPVerifyView.as_view(), name='driver-seller-otp-verify'),


]