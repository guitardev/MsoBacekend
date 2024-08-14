# main/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProfileViewSet, LoginMethodViewSet, CustomTokenObtainPairView, UserCreate 


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'login', LoginMethodViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/register/', UserCreate.as_view()),  # ยังคงใช้ UserCreate แยกต่างหาก
]
