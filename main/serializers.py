# main/serializers.py

from rest_framework import serializers
from .models import CustomUser, Profile, LoginMethod
from django.contrib.auth.hashers import make_password
from django.utils import timezone


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer สำหรับโมเดล CustomUser 
    จัดการการสร้างผู้ใช้, การเข้ารหัสรหัสผ่าน, และไม่รวมฟิลด์ที่ละเอียดอ่อนจากการตอบสนอง
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'national_id', 'phone_number', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # ซ่อน password ใน response

    def create(self, validated_data):
        """
        แทนที่เมธอด create เพื่อเข้ารหัสรหัสผ่านก่อนบันทึกผู้ใช้
        """
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):
        """
        ตรวจสอบความแข็งแกร่งของรหัสผ่าน คุณสามารถเพิ่มตรรกะการตรวจสอบรหัสผ่านที่ซับซ้อนมากขึ้นได้ที่นี่
        """
        if len(value) < 8:
            raise serializers.ValidationError("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร ")
        return value

    def to_representation(self, instance):
        """
        แทนที่ to_representation เพื่อไม่รวมฟิลด์ที่ละเอียดอ่อนเช่นรหัสผ่านออกจากการตอบสนอง
        """
        ret = super().to_representation(instance)
        ret.pop('password')  # Remove password from the response
        return ret

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer สำหรับโมเดล Profile รวมถึง URL ของ avatar และตรวจสอบความถูกต้องของวันเกิด
    """
    avatar_url = serializers.SerializerMethodField()  # เพิ่ม SerializerMethodField สำหรับ URL ของรูปภาพ

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'avatar', 'avatar_url', 'birth_date']  # เพิ่ม 'avatar_url' ใน fields
        read_only_fields = ['user']

    def get_avatar_url(self, obj):
        """
        รับ URL เต็มของรูปภาพ avatar
        """
        if obj.avatar:
            return obj.avatar.url
        return None
    
    def validate_birth_date(self, value):
        """
        ตรวจสอบว่าวันเกิดไม่ได้อยู่ในอนาคต
        """
        if value and value > timezone.now().date():
            raise serializers.ValidationError("วันเกิดไม่สามารถอยู่ในอนาคตได้ ")
        return value

class LoginMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginMethod
        fields = ['id', 'user', 'login_type', 'identifier']
        read_only_fields = ['user']  # Make 'user' field read-only

class TokenObtainPairSerializer(serializers.Serializer):
    """
    Serializer สำหรับโมเดล LoginMethod ฟิลด์ 'user' เป็นแบบอ่านอย่างเดียว
    """
    email = serializers.EmailField(required=False)
    national_id = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        ตรวจสอบข้อมูลประจำตัวการเข้าสู่ระบบและส่งคืนออบเจ็กต์ผู้ใช้หากสำเร็จ
        """
        # Check if at least one identifier is provided
        if not any([attrs.get('email'), attrs.get('national_id'), attrs.get('phone_number')]):
            raise serializers.ValidationError("คุณต้องระบุตัวระบุอย่างน้อยหนึ่งรายการ (อีเมล์, หมายเลขบัตรประจำตัว, หรือ หมายเลขโทรศัพท์).")

        # Try to find the user based on the provided identifier
        user = None
        if attrs.get('email'):
            user = CustomUser.objects.filter(email=attrs['email']).first()
        elif attrs.get('national_id'):
            user = CustomUser.objects.filter(national_id=attrs['national_id']).first()
        elif attrs.get('phone_number'):
            user = CustomUser.objects.filter(phone_number=attrs['phone_number']).first()

        if user and user.check_password(attrs['password']):
            if not user.is_active:
                raise serializers.ValidationError("บัญชีผู้ใช้ถูกปิดใช้งาน.")  # เพิ่ม error message สำหรับ user ที่ไม่ active
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง.")  # ปรับปรุง error message
