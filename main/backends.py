# main/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import LoginMethod
from rest_framework.exceptions import AuthenticationFailed
import logging

# สร้าง logger
logger = logging.getLogger(__name__)

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # ลองค้นหาผู้ใช้ใน LoginMethod ก่อน
            login_method = LoginMethod.objects.get(identifier=username)
            user = login_method.user
            logger.info(f"User {user} attempted login using {login_method.login_type}.") 
        except LoginMethod.DoesNotExist:
            # ถ้าไม่พบใน LoginMethod ให้ลองค้นหาด้วย email
            try:
                user = User.objects.get(email=username)
                logger.info(f"User {user} attempted login using email.") 
            except User.DoesNotExist:
                logger.warning(f"Authentication failed: User with identifier '{username}' not found.")
                raise AuthenticationFailed("Invalid credentials.")  # ส่งคืน error message หากไม่พบผู้ใช้

        if not user.is_active:
            logger.warning(f"Authentication failed: User {user} is inactive.")
            raise AuthenticationFailed("User account is disabled.")  # ส่งคืน error message หากผู้ใช้ไม่ active

        if user.check_password(password):
            logger.info(f"User {user} logged in successfully.")
            return user
        else:
            logger.warning(f"Authentication failed: Incorrect password for user {user}.")
            raise AuthenticationFailed("Invalid credentials.")  # ส่งคืน error message หากรหัสผ่านไม่ถูกต้อง
