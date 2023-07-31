from django.db import models
from django.urls import reverse
from accounts.models import CustomUser


# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    captain = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='team_captain')
    players = models.ManyToManyField(CustomUser, related_name='player', blank=True)

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse('tournament:team_detail', kwargs={'pk': self.id})