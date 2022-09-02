from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

class User(AbstractUser):
    def str(self):
        return self.username
