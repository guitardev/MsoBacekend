# main/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)  # สร้าง logger สำหรับบันทึกข้อผิดพลาด

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    สร้าง Profile object ใหม่เมื่อมีการสร้าง CustomUser object ใหม่
    หากเกิดข้อผิดพลาด IntegrityError จะบันทึก log และข้ามการสร้าง Profile
    """
    if created:
        try:
            Profile.objects.create(user=instance)
        except IntegrityError as e:
            logger.error(f"Failed to create profile for user {instance.id}: {e}")

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    บันทึก Profile object เมื่อมีการบันทึก CustomUser object
    หาก Profile ยังไม่ถูกสร้าง จะสร้าง Profile ใหม่
    หากเกิดข้อผิดพลาด IntegrityError หรืออื่นๆ จะบันทึก log และข้ามการบันทึก
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
    except IntegrityError as e:
        logger.error(f"Failed to save profile for user {instance.id}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while saving profile for user {instance.id}: {e}")
