from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import BaseModel


class User(AbstractUser):
    user_type = models.CharField(null=True, max_length=255)
    email = models.CharField(blank=True, max_length=255, unique=True)
    username = models.CharField(null=True, max_length=255)
    password = models.CharField(null=True, max_length=128)
    email_confirmed = models.BooleanField(blank=False, default=False)
    overview = models.TextField(null=True)
    avatar = models.TextField(null=True)
    mobile = models.CharField(null=True, max_length=255)
    password_reset_token = models.IntegerField(null=True)
    password_reset_sent_at = models.DateTimeField(null=True)
    customer_id = models.CharField(null=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
