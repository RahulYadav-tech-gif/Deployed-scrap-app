from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ValidationError
from .models import User

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_verified:
            raise ValidationError ("This account is not Verified. Please verify your email first.", code='inactive')