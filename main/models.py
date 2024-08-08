# main/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.validators import RegexValidator

# custom validator for username
alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for managing CustomUser model.
    """

    def create_user(self, email=None, password=None, national_id=None, phone_number=None, **extra_fields):
        # ... (ตรวจสอบว่ามีอย่างน้อยหนึ่ง identifier)

        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, national_id=national_id, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Retrieve a user by their username (email, national_id, or phone_number).
        """
        return self.get(
            Q(email=username) |
            Q(national_id=username) |
            Q(phone_number=username)
        )

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email, national ID, or phone number as username.
    """
    email = models.EmailField(_("email"), unique=True, blank=True, null=True)
    national_id = models.CharField(_("national ID"), validators=[alphanumeric], max_length=13, unique=True, blank=True, null=True)
    phone_number = PhoneNumberField(_("phone number"), unique=True, blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # สามารถเปลี่ยนเป็น 'national_id' หรือ 'phone_number' ได้ตามต้องการ
    REQUIRED_FIELDS = []

    def __str__(self):
        """
        Return a string representation of the user.
        """
        if self.email:
            return f"{self.email} ({self.first_name} {self.last_name})"
        elif self.national_id:
            return f"{self.national_id} ({self.first_name} {self.last_name})"
        elif self.phone_number:
            return f"{self.phone_number} ({self.first_name} {self.last_name})"
        else:
            return "Unknown User"

    def set_password(self, raw_password):
        """
        Hash the password before saving.
        """
        self.password = make_password(raw_password)
        self._password = raw_password  # Store the unhashed password temporarily for validation

class LoginMethod(models.Model):
    """
    Model to store different login methods for a user.
    """
    EMAIL = 'email'
    NATIONAL_ID = 'national_id'
    PHONE_NUMBER = 'phone_number'
    LOGIN_TYPE_CHOICES = [
        (EMAIL, _("email")),
        (NATIONAL_ID, _("national ID")),
        (PHONE_NUMBER, _("phone number")),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_methods')
    login_type = models.CharField(max_length=15, choices=LOGIN_TYPE_CHOICES)
    identifier = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.user} - {self.get_login_type_display()}: {self.identifier}"


class Profile(models.Model):
    """
    Model to store additional user profile information.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_("bio"), blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(_("birth date"), null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s profile"
