from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
import json
from google.oauth2.credentials import Credentials
from django.conf import settings

class CustomUser(AbstractUser):
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

class UserCredentials(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()
    credentials = models.TextField()  # Lưu thông tin xác thực dưới dạng JSON

    def get_credentials(self):
        credentials_dict = json.loads(self.credentials)
        creds = Credentials(
            token=credentials_dict['token'],
            refresh_token=credentials_dict['refresh_token'],
            token_uri=credentials_dict['token_uri'],
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret'],
            scopes=credentials_dict['scopes']
        )
        return creds

    def save_credentials(self, creds):
        creds_json = json.dumps({
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        })
        self.credentials = creds_json
        self.save()