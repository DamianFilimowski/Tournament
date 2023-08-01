from django.db import models
from django.urls import reverse
from accounts.models import CustomUser


# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=8)
    captain = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='team_captain')
    players = models.ManyToManyField(CustomUser, related_name='player', blank=True)

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse('tournament:team_detail', kwargs={'pk': self.id})


class Tournament(models.Model):

    tournament_admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    max_teams_amount = models.IntegerField()
    teams = models.ManyToManyField(Team, blank=True)
    phases_drawn = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse('tournament:tournament_detail', kwargs={'pk': self.id})


class Match(models.Model):
    RESULT_CHOICES = (
        (1, 'Team 1 Wins'),
        (0, 'Draw'),
        (2, 'Team 2 Wins'),
    )
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    order = models.IntegerField()
    phase = models.IntegerField()
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')
    team1_score = models.PositiveIntegerField(default=0)
    team2_score = models.PositiveIntegerField(default=0)
    result = models.IntegerField(choices=RESULT_CHOICES, null=True, default=None)
    match_date = models.DateTimeField(null=True, blank=True)
    is_group = models.BooleanField(default=False)

    def __str__(self):
        if self.result is not None:
            return f"{self.team1.name} - {self.team2.name} {self.team1_score}:{self.team2_score}"
        else:
            return f"{self.team1.name} vs. {self.team2.name} - {self.date}"

    class Meta:
        unique_together = ['order', 'tournament']

    def get_detail_url(self):
        return reverse('tournament:match_detail', kwargs={'pk': self.id})


class Scorers(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    scorer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    minute = models.IntegerField()