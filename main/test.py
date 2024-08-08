# main/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, LoginMethod
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db import IntegrityError
import datetime , time

User = get_user_model()

class UserModelTestCase(TestCase):
    def test_create_user(self):
        """
        ทดสอบการสร้าง user ปกติ
        """
        user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        ทดสอบการสร้าง superuser
        """
        superuser = User.objects.create_superuser(email='testsuperuser@example.com', password='testpassword')
        self.assertEqual(superuser.email, 'testsuperuser@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_with_national_id(self):
        """
        ทดสอบการสร้าง user ด้วย national_id
        """
        user = User.objects.create_user(national_id='1234567890123', password='testpassword')
        self.assertEqual(user.national_id, '1234567890123')

    def test_create_user_with_phone_number(self):
        """
        ทดสอบการสร้าง user ด้วย phone_number
        """
        user = User.objects.create_user(phone_number='+66812345678', password='testpassword')
        self.assertEqual(str(user.phone_number), '+66812345678')

    def test_get_by_natural_key(self):
        """
        ทดสอบการค้นหา user ด้วย get_by_natural_key
        """
        user = User.objects.create_user(email='testuser2@example.com', password='testpassword')
        self.assertEqual(User.objects.get_by_natural_key('testuser2@example.com'), user)

class ProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser3@example.com', password='testpassword')
        self.profile, _ = Profile.objects.get_or_create(user=self.user, bio='Test bio') 

    def test_create_profile(self):
        """
        ทดสอบการสร้าง profile (ไม่ควรสร้างใหม่เพราะมี profile อยู่แล้ว)
        """
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user, bio='Test bio')

    def test_update_profile(self):
        """
        ทดสอบการแก้ไข profile
        """
        self.profile.bio = 'Updated bio'
        self.profile.save()
        self.assertEqual(Profile.objects.get(user=self.user).bio, 'Updated bio')

    def test_profile_avatar_upload(self):
        """
        ทดสอบการอัปโหลดรูปภาพ avatar
        """
        timestamp = int(time.time())
        with open("tests/test_image.jpg", "rb") as image_file:  # แทนที่ด้วย path ที่ถูกต้องของรูปภาพที่คุณมี
            self.profile.avatar = SimpleUploadedFile(name=f'test_avatar_{timestamp}.jpg', content=image_file.read(), content_type='image/jpeg')
            self.profile.save()
        self.assertTrue(self.profile.avatar)
        self.assertEqual(self.profile.avatar.url, f'/media/avatars/test_avatar_{timestamp}.jpg')


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser4@example.com', password='testpassword')
        LoginMethod.objects.create(user=self.user, login_type=LoginMethod.EMAIL, identifier=self.user.email)

    def test_login_with_email(self):
        """
        ทดสอบการ login ด้วย email
        """
        response = self.client.post('/api/token/', {'email': self.user.email, 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_national_id(self):
        """
        ทดสอบการ login ด้วย national_id
        """
        # สร้าง LoginMethod สำหรับ national_id ก่อน
        LoginMethod.objects.create(user=self.user, login_type=LoginMethod.NATIONAL_ID, identifier='1234567890123')
        self.user.national_id = '1234567890123'
        self.user.save()

        response = self.client.post('/api/token/', {'national_id': self.user.national_id, 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_phone_number(self):
        """
        ทดสอบการ login ด้วย phone_number
        """
        # สร้าง LoginMethod สำหรับ phone_number ก่อน
        LoginMethod.objects.create(user=self.user, login_type=LoginMethod.PHONE_NUMBER, identifier='+66812345678')
        self.user.phone_number = '+66812345678'
        self.user.save()

        response = self.client.post('/api/token/', {'phone_number': str(self.user.phone_number), 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class APIViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(email='testuser5@example.com', password='testpassword')
        cls.token = RefreshToken.for_user(cls.user).access_token

        # สร้าง profile ก่อน
        Profile.objects.create(user=cls.user, bio='Test bio')

        # จากนั้นค่อยใช้ get_or_create เพื่อดึง profile ที่สร้างขึ้นมา
        cls.profile, _ = Profile.objects.get_or_create(user=cls.user) 

        # สร้าง admin user
        cls.admin_user = User.objects.create_superuser(email='admin@example.com', password='adminpassword')
        cls.admin_token = RefreshToken.for_user(cls.admin_user).access_token

    def setUp(self):
        self.client = APIClient()

    def test_user_viewset(self):
        """
        ทดสอบ UserViewSet
        """
        # list: ต้องเป็น admin ถึงจะดูได้
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 403)  # Forbidden (user ปกติ)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # retrieve: ต้อง login
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 401)  # Unauthorized (ยังไม่ login)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)

        # create: อนุญาตให้ทุกคนสร้าง
        data = {'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 3)

        # update: ต้อง login และเป็นเจ้าของ user
        new_data = {'first_name': 'UpdatedFirstName', 'last_name': 'UpdatedLastName'}
        response = self.client.put(f'/api/users/{self.user.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 401)  # Unauthorized (ยังไม่ login)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(f'/api/users/{self.user.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'UpdatedFirstName')
        self.assertEqual(updated_user.last_name, 'UpdatedLastName')

        # partial_update: เหมือนกับ update แต่ส่งเฉพาะ fields ที่ต้องการแก้ไข
        new_data = {'first_name': 'UpdatedFirstNameAgain'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.patch(f'/api/users/{self.user.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'UpdatedFirstNameAgain')
        self.assertEqual(updated_user.last_name, 'UpdatedLastName') 

        # destroy: ต้อง login และเป็นเจ้าของ user หรือเป็น admin
        response = self.client.delete(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 401)  # Unauthorized (ยังไม่ login)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.delete(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, 204)  # No Content
        self.assertEqual(User.objects.count(), 2)  # ลบ user ไป 1 คน

    def test_user_create(self):
        """
        ทดสอบ endpoint UserCreate
        """
        data = {'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(User.objects.count(), 3)  # มี 3 users ในระบบ

    def test_user_update(self):
        """
        ทดสอบ endpoint UserUpdate (ต้อง login)
        """
        # ลองเข้าถึงโดยไม่ login
        new_data = {'first_name': 'UpdatedFirstName', 'last_name': 'UpdatedLastName'}
        response = self.client.put(f'/api/users/{self.user.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 401)  # Unauthorized

        # ลองเข้าถึงด้วย user ที่ login แล้ว
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(f'/api/users/{self.user.id}/', new_data, format='json')
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบว่าข้อมูลถูกอัพเดตแล้ว
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'UpdatedFirstName')
        self.assertEqual(updated_user.last_name, 'UpdatedLastName')

    def test_profile_detail(self):
        """
        ทดสอบ endpoint ProfileDetail (ต้อง login)
        """
        # ลองเข้าถึงโดยไม่ login
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)  # Unauthorized

        # ลองเข้าถึงด้วย user ที่ login แล้ว
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['bio'], self.profile.bio)

        # ทดสอบการแก้ไข profile
        new_bio = 'Updated bio'
        response = self.client.put('/api/profile/', {'bio': new_bio}, format='json')
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบว่าข้อมูลถูกอัพเดตแล้ว
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, new_bio)

    def test_login_method_list_and_create(self):
        """
        ทดสอบ endpoint LoginMethodList (ต้อง login)
        """
        # ลองเข้าถึงโดยไม่ login
        response = self.client.get('/api/login-methods/')
        self.assertEqual(response.status_code, 401)  # Unauthorized

        # ลองเข้าถึงด้วย user ที่ login แล้ว
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/api/login-methods/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # มี 1 login method ในระบบ (จากการ setUp)

        # ทดสอบการสร้าง LoginMethod ใหม่
        new_login_method_data = {'login_type': LoginMethod.NATIONAL_ID, 'identifier': '1234567890123'}
        response = self.client.post('/api/login-methods/', new_login_method_data, format='json')
        self.assertEqual(response.status_code, 201)  # Created
        self.assertEqual(LoginMethod.objects.count(), 2)  # มี 2 login methods ในระบบ

    def test_login_method_detail(self):
        """
        ทดสอบ endpoint LoginMethodDetail (ต้อง login และเป็นเจ้าของ)
        """
        login_method = LoginMethod.objects.get(user=self.user)  # ดึง LoginMethod ที่สร้างไว้ตอน setUp

        # ลองเข้าถึงโดยไม่ login
        response = self.client.get(f'/api/login-methods/{login_method.id}/')
        self.assertEqual(response.status_code, 401)  # Unauthorized

        # ลองเข้าถึงด้วย user ที่ login แล้ว
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(f'/api/login-methods/{login_method.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['identifier'], self.user.email)

        # ทดสอบการแก้ไข LoginMethod (ควรจะทำไม่ได้เพราะเป็น read-only fields)
        new_identifier = 'updated_email@example.com'
        response = self.client.put(f'/api/login-methods/{login_method.id}/', {'identifier': new_identifier}, format='json')
        self.assertEqual(response.status_code, 200)  # อนุญาตให้แก้ไข แต่ค่าไม่ควรเปลี่ยนแปลง
        updated_login_method = LoginMethod.objects.get(id=login_method.id)
        self.assertEqual(updated_login_method.identifier, self.user.email)

        # ทดสอบการลบ LoginMethod
        response = self.client.delete(f'/api/login-methods/{login_method.id}/')
        self.assertEqual(response.status_code, 204)  # No Content
        self.assertEqual(LoginMethod.objects.count(), 0)  # ไม่เหลือ login method ในระบบ
 
