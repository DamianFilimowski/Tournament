from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

# Create your models here.


class CustomUser(AbstractUser):
    goals = models.IntegerField(default=0)

    def get_detail_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.id})