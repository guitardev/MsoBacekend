# main/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class CustomLoginForm(AuthenticationForm):
    """
    Custom login form that allows login with email, national ID, or phone number.
    """
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    # ไม่จำเป็นต้องมีฟิลด์สำหรับ national_id และ phone_number 
    # เพราะเราจะใช้ฟิลด์ username เดียวในการรับข้อมูลทั้งหมด
