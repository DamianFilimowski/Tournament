from django.core.exceptions import ValidationError
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
        (3, 'Mecz nierozegrany'),
    )
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    order = models.IntegerField()
    phase = models.IntegerField()
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches', null=True, blank=True)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches', null=True, blank=True)
    team1_score = models.PositiveIntegerField(default=None, null=True, blank=True)
    team2_score = models.PositiveIntegerField(default=None, null=True, blank=True)
    result = models.IntegerField(choices=RESULT_CHOICES, null=True, default=3)
    match_date = models.DateTimeField(null=True, blank=True)
    is_group = models.BooleanField(default=False)


    def get_detail_url(self):
        return reverse('tournament:match_detail', kwargs={'pk': self.id})

    def clean(self):
        if self.team1 == self.team2:
            raise ValidationError("Team 1 and Team 2 cannot be the same.")


class Scorers(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    scorer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    minute = models.IntegerField()

    def __str__(self):
        return f'Strzelec bramki: {self.scorer} z {self.minute} minuty, w meczu {self.match}'


class GroupStage(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    promoted_teams = models.ManyToManyField(Team, related_name='promoted_teams')
    matches = models.ManyToManyField(Match, related_name='matches')
    matches_finished = models.ManyToManyField(Match)

    def __str__(self):
        return f"{self.tournament} - {self.name}"

    def get_detail_url(self):
        return reverse('tournament:groupstage_detail', kwargs={'pk': self.id})


class Playoff(models.Model):

    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE)
    matches = models.ManyToManyField(Match)

    def __str__(self):
        return f"Play-off dla {self.tournament}"
