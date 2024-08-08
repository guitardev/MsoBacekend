# main/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import LoginMethod

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            login_method = LoginMethod.objects.get(identifier=username)
            user = login_method.user
        except LoginMethod.DoesNotExist:
            # ถ้าไม่พบใน LoginMethod ให้ลองค้นหาด้วย email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
