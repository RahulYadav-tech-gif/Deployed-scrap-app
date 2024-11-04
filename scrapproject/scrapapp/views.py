from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import authenticate, login
# from rest_framework.authtoken.models import Token
# from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, views as auth_views
from .forms import CustomAuthenticationForm
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics
import razorpay
from random import choice

# Create your views here.

def payment_view(request):
    print("Payment")
    return render(request, 'payment.html')

User = get_user_model()

class AllDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({"status":200, "payload":serializer.data})
    

# Sign Up

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = OTP.objects.create(user=user)
            otp.generate_otp()

            send_mail(
                subject = 'Your OTP Code',
                message = f'Your otp code is {otp.otp_code}',
                from_email='rahulyadav.arcade@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"message":"OTP sent to your email."}, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Otp verify

class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                otp = OTP.objects.filter(user=user).latest('created_at')
                if otp.otp_code == serializer.validated_data['otp_code'] and otp.is_valid():
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    # send_mail(
                    #     subject='New User Approval Needed',
                    #     message=f'User {user.username} has verified their account and is awaiting approval.',
                    #     from_email=settings.DEFAULT_FROM_EMAIL,
                    #     recipient_list=['rahulyadav.arcade@gmail.com'],  
                    #     fail_silently=False,
                    # )
                    refresh = RefreshToken.for_user(user)

                    return Response({"message":"Account verified.", 'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response({"error":"Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)


            except User.DoesNotExist:
                return Response({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# Sign In

class SigninView(APIView, auth_views.LoginView):
    def post(self, request):
        data = request.data
        serializer = SigninSerializer(data=data)
        if not serializer.is_valid():
            return Response({'status':False, "data":serializer.errors})
        
        
        
        # username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        

        form = CustomAuthenticationForm(data={'username': email, 'password': password})

        if not form.is_valid():
            return Response({'status': False, 'error': form.errors}, status=400)

        user = form.get_user()


        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=400)

        if user:
            user_obj = authenticate( email=email, password=password)
        
        if user_obj:
            refresh = RefreshToken.for_user(user)
            return Response({'status':True, 'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return Response({"error":"User does not exist or password incorrect"})
        
# Forgot Password

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status':False, "data":serializer.errors})
        
        email = serializer.validated_data['email']

        
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                return Response({"error": "This account is not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
            

            otp = OTP.objects.create(user=user)
            otp.generate_otp()

            send_mail(
                subject = 'Your Password-Reset OTP Code',
                message = f'Your password-reset otp code is {otp.otp_code}',
                from_email='rahulyadav.arcade@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"message":"OTP sent to your email."}, status=status.HTTP_201_CREATED )
        
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=400)


# Reset Password Otp verify

class ResetPasswordOTPVerifyView(APIView):
    def post(self, request, id):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                email=serializer.validated_data['email']
                user = User.objects.get(email=email, id=id)
                if not user.is_verified:
                    return Response({"error": "This account is not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
                otp = OTP.objects.filter(user=user).latest('created_at')
                if otp.otp_code == serializer.validated_data['otp_code'] and otp.is_valid():
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    
                    return Response({"message":"OTP Verified."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error":"Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)


            except User.DoesNotExist:
                return Response({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# Reset Password 

class ResetPasswordView(APIView):
    def post(self, request, id):
        serializer = NewPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = request.data.get('email')

            try:
                user = User.objects.get(email=email, id=id)
                if not user.is_verified:
                    return Response({"error": "This account is not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
                
                serializer.save(user=user)

                return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Scrap Product

class ScrapProductView(viewsets.ModelViewSet):
    queryset = ScrapProduct.objects.all()
    serializer_class = ScrapProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
        

# Category 

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# Condition api

class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    permission_classes = [IsAuthenticated]


# Driver view set

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer 
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)  
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                
                send_mail(
                    subject='New User Approval Needed',
                    message=f'User {user.username} has verified their account and is awaiting approval.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['rahulyadav.arcade@gmail.com'],
                    fail_silently=False,
                )
                return Response({"message": "Wait for admin approval"}, status=status.HTTP_201_CREATED)

            except User.DoesNotExist:
                return Response({"message": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_drivers = Driver.objects.filter(availability=True)

        if not available_drivers.exists():
            return Response({"message": "No available drivers found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(available_drivers, many=True)

        return Response(serializer.data)
    

    @action(detail=False, methods=['post'])
    def assign_driver(self, request):
        driver_id = request.data.get('driver_id')
        product_id = request.data.get('product_id')

        if not driver_id:
            return Response({"message": "Driver id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not product_id:
            return Response({"message": "Product id is required"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            selected_driver = Driver.objects.get(id=driver_id)

        except Driver.DoesNotExist:
            return Response({"message": "Driver does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        product = ScrapProduct.objects.get(id=product_id)

        self.send_email_to_driver(selected_driver, product)

        return Response({"message": "Email sent to the driver"}, status=status.HTTP_200_OK)


    
    def send_email_to_driver(self, driver, product):
        user = driver.driver
        seller_name = product.seller
        try:
            send_mail(
                subject='Product Collection Request',
                message=f"Hello {user.first_name} {user.last_name},\n\n"
                        f"You have been assigned to collect a product from a seller.\n\n"
                        f"Seller details:-\n"
                        f"Seller Name: {seller_name.first_name} {seller_name.last_name}\n"
                        f"Seller Phone no.: {seller_name.phone_number}\n"
                        f"Seller Address: {seller_name.address}\n\n"
                        f"Product Details:-\n"
                        f"Product Name: {product.productName}\n"
                        f"Product Category: {product.productCategory}\n"
                        f"Product Price: {product.productPrice}\n"
                        f"Product Quantity: {product.productQuantity}\n\n"

                        f"If you are available please call the admin within 2-3 days.\n\n"
                        f"Thank you!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    

class InformSeller(APIView):
    def post(self, request):
        driver_id = request.data.get('driver_id')
        product_id = request.data.get('product_id')
        arrival_date = request.data.get('arrival_date')

        try:
            driver = Driver.objects.get(id=driver_id)
            product = ScrapProduct.objects.get(id=product_id)
            seller = product.seller

            assignment = CollectionDetail.objects.create(driver_name=driver, product_name=product, seller_name=seller, arrival_date=arrival_date)

            driver.availability = False
            driver.save()

            driver_name = driver.driver
            seller_name = product.seller
            try:
                send_mail(
                    subject='Driver Assigned for Collect Product',
                    message=f"Hello {seller_name.first_name} {seller_name.last_name},\n\n"
                            f"Driver has been assigned to collect your product: {product.productName}.\n\n"
                            f"Driver details:-\n"
                            f"Driver Name: {driver_name.first_name} {driver_name.last_name}\n"
                            f"Driver Phone no.: {driver_name.phone_number}\n"
                            f"Driver vehicle number: {driver.vehicleNumber}\n"
                            f"Arrival Date: {arrival_date}\n\n"
                            f"Thank you!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[seller_name.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {str(e)}")
            
            
            serializer = CollectionDetailSerializer(assignment)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except (Driver.DoesNotExist, ScrapProduct.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        


class DriverSellerOTPView(APIView):
    def post(self, request):
        driver_id = request.data.get('driver_id')
        product_id = request.data.get('product_id')

        try:
            driver = Driver.objects.get(id=driver_id)
            product = ScrapProduct.objects.get(id=product_id)
            seller = product.seller

            driver_name = driver.driver
            print(seller.first_name)
            try:
                user = User.objects.get(email=seller.email)
                if not user.is_verified:
                    return Response({"error": "This account is not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
                
                otp = OTP.objects.create(user=user)
                otp.generate_otp()

                print(driver_name.email)   
                send_mail(
                    subject='Product Collection OTP',
                    message=f"Hello {seller.first_name} {seller.last_name},\n\n"
                            f"The OTP to collect your product: {product.productName} is {otp.otp_code}.\n\n",
                        
                    from_email=driver_name.email,
                    recipient_list=[seller.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {str(e)}")
            

            return Response({'message: OTP has been sent'}, status=status.HTTP_200_OK)
        
        except (Driver.DoesNotExist, ScrapProduct.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)



class DriverSellerOTPVerifyView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = CollectionDetail.objects.get(product_name=product_id)
                user = User.objects.get(email=serializer.validated_data['email'])
                otp = OTP.objects.filter(user=user).latest('created_at')
                if otp.otp_code == serializer.validated_data['otp_code'] and otp.is_valid():
                    product.is_collected = True
                    product.save()
                    return Response({"message":"OTP verified."}, status=status.HTTP_200_OK)
                
                else:
                    return Response({"error":"Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)


            except User.DoesNotExist:
                return Response({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class CreateOrderView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')  

        if product_id is None:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = ScrapProduct.objects.get(id=product_id)
            # amount = product.productPrice * product.productQuantity
             
  
            try:
                send_mail(
                    subject="Purchase Confirmation and Delivery Details",
                    message=f"Dear {product.seller.first_name} {product.seller.last_name},\n\n"

                    f"I hope this message finds you well.\n\n"

                    f"I am pleased to inform you that our admin team is impressed with your product and has decided to proceed with the purchase. A driver will be assigned to pick up the product shortly.\n\n"

                    f"We will send you the driver’s details and their estimated arrival time soon. Please note that payment will be processed after the driver successfully receives the product.\n\n"

                    f"Thank you for your cooperation. If you have any questions or need further assistance, please feel free to reach out.\n",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[product.seller.email],
                    fail_silently=False
                
                )
                return Response({"message":"Mail has been sent"}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            # order = client.order.create({
            #     'amount': amount,  
            #     'currency': 'INR',
            #     'payment_capture': '1'  
            # })
            # return Response(order, status=status.HTTP_201_CREATED)

        except ScrapProduct.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class Payment(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        print("Razorpay API Key:", settings.RAZORPAY_API_KEY)
        print("Razorpay API Secret:", settings.RAZORPAY_API_SECRET)
        if product_id is None:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = ScrapProduct.objects.get(id=product_id)
            amount = product.productPrice * product.productQuantity * 100
            
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
          
            payment_order = client.order.create({
                'amount':amount,
                'currency':'INR',
                'payment_capture':'1',

            })
            payment_order_id = payment_order['id']
            context = {
                'amount':amount, 'api_key':settings.RAZORPAY_API_KEY, 'order_id':payment_order_id
            }
            # payment = Payment.objects.create(order_id=razorpay_order_id, payment_id=razorpay_payment_id, signature=razorpay_signature)

            return Response(context, status=status.HTTP_200_OK)

        except ScrapProduct.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class PaymentVerificationView(APIView):
    def post(self, request):
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            # Save payment information
            payment = Payment.objects.create(order_id=order_id, payment_id=payment_id, signature=signature)
            Transaction.objects.create(payment=payment, amount=request.data.get('amount'), status='successful')

            return Response({'status': 'Payment verified'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
