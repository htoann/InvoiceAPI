from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
import json
from google.oauth2.credentials import Credentials
from django.conf import settings

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

class CustomUser(AbstractUser):
    permission_classes = [AllowAny]

    email_password = models.CharField(max_length=100)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Thay đổi related_name để tránh xung đột
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Thay đổi related_name để tránh xung đột
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )

class MailAccount(models.Model):
    name = models.TextField()
    email = models.EmailField()
    credentials = models.JSONField() 

    def get_credentials(self):
        return Credentials(**self.credentials)


class MailInbox(models.Model):
    mail_account = models.ForeignKey(MailAccount, on_delete=models.CASCADE)
    subject = models.TextField()
    sender = models.TextField()
    date = models.DateTimeField()
    label = models.TextField()