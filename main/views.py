from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, ProfileSerializer, LoginMethodSerializer,TokenObtainPairSerializer
from .models import CustomUser, Profile, LoginMethod
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied , NotFound

class UserCreate(generics.CreateAPIView):
    """
    API endpoint สำหรับสร้างผู้ใช้ใหม่ อนุญาตให้ทุกคนเข้าถึงได้
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet สำหรับจัดการ CustomUser
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
class ProfileViewSet(viewsets.ModelViewSet): 

    """
    ViewSet สำหรับจัดการ Profile
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer): 

        serializer.save(user=self.request.user)
        
        
class ProfileDetail(generics.RetrieveUpdateAPIView):
    """
    API endpoint สำหรับดูและแก้ไข profile ของผู้ใช้ที่ล็อกอินอยู่
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist: 
            raise NotFound("Profile not found. Please create one.")
class LoginMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet สำหรับจัดการ LoginMethod
    """
    serializer_class = LoginMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.login_methods.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint สำหรับ login (ขอ JWT token) โดยใช้ email, national_id, หรือ phone_number
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # ตรวจสอบว่า error เกิดจากการ login ผิดพลาดหรือไม่
            if 'no active account' in str(e).lower():
                return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise e

        user = serializer.validated_data['user']

        if not user.is_active:
            return Response({'detail': 'User account is disabled.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        login_type_mapping = {
            'email': LoginMethod.EMAIL,
            'national_id': LoginMethod.NATIONAL_ID,
            'phone_number': LoginMethod.PHONE_NUMBER,
        }

        login_type = login_type_mapping.get(next((key for key in request.data if key in login_type_mapping), None))

        if not login_type:
            return Response({'detail': 'Unsupported login type.'}, status=status.HTTP_400_BAD_REQUEST)

        identifier = request.data.get(login_type)

        try:
            # ปรับปรุงการสร้างหรือดึง LoginMethod object
            login_method, _ = LoginMethod.objects.update_or_create(
                user=user,
                login_type=login_type,
                defaults={'identifier': identifier}
            )
        except IntegrityError:
            return Response({'detail': 'This identifier is already associated with another user.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)

class LoginMethodList(generics.ListCreateAPIView):
    """
    API endpoint สำหรับดูและสร้างวิธีการ login ของผู้ใช้ที่ล็อกอินอยู่
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LoginMethodSerializer

    def get_queryset(self):
        return self.request.user.login_methods.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LoginMethodDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint สำหรับดู, แก้ไข, และลบวิธีการ login ที่ระบุ (เฉพาะเจ้าของ)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LoginMethodSerializer

    def get_queryset(self):
        return self.request.user.login_methods.all().select_related('user')  # ใช้ select_related เพื่อเพิ่มประสิทธิภาพ

    def get_object(self):
        """
        Retrieve the LoginMethod object and check if it belongs to the authenticated user.
        """
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this login method.")
        return obj
