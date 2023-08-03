import math
import random

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View

from tournament.models import *


# Create your views here.

class TeamListView(ListView):
    model = Team
    template_name = 'tournament/team_list.html'


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'tournament/form.html'
    fields = ['name', 'short_name']
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        form.instance.captain = self.request.user
        return super().form_valid(form)


class TeamDetailView(DetailView):
    model = Team
    template_name = 'tournament/team_detail.html'


class TeamUpdateView(UserPassesTestMixin, UpdateView):
    model = Team
    template_name = 'tournament/form.html'
    fields = ['name', 'short_name']

    def test_func(self):
        team = self.get_object()
        return self.request.user == team.captain

    def get_success_url(self):
        return reverse_lazy('tournament:team_detail', kwargs={'pk': self.object.id})


class TeamDeleteView(UserPassesTestMixin, DeleteView):
    model = Team
    success_url = reverse_lazy('accounts:profile')

    def test_func(self):
        team = self.get_object()
        return self.request.user == team.captain


class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournament/tournament_list.html'


class TournamentCreateView(LoginRequiredMixin, CreateView):
    model = Tournament
    template_name = 'tournament/form.html'
    fields = ['name', 'max_teams_amount']
    success_url = reverse_lazy('tournament:tournament_list')

    def form_valid(self, form):
        form.instance.tournament_admin = self.request.user
        return super().form_valid(form)


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'tournament/tournament_detail.html'


class TournamentUpdateView(UserPassesTestMixin, UpdateView):
    model = Tournament
    template_name = 'tournament/form.html'
    fields = ['name', 'max_teams_amount', 'teams']

    def test_func(self):
        tournament = self.get_object()
        return self.request.user == tournament.tournament_admin

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.id})


class TournamentDeleteView(UserPassesTestMixin, DeleteView):
    model = Tournament
    success_url = reverse_lazy('accounts:profile')

    def test_func(self):
        tournament = self.get_object()
        return self.request.user == tournament.tournament_admin


class MatchDetailView(DetailView):
    model = Match
    template_name = 'tournament/match_detail.html'


class MatchUpdateResultView(UserPassesTestMixin, UpdateView):
    model = Match
    template_name = 'tournament/form.html'
    fields = ['team1_score', 'team2_score']

    def test_func(self):
        match = self.get_object()
        return self.request.user == match.tournament.tournament_admin

    def form_valid(self, form):
        if self.object.team1_score > self.object.team2_score:
            self.object.result = 1
        elif self.object.team1_score < self.object.team2_score:
            self.object.result = 2
        else:
            self.object.result = 0
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.object.id})


class MatchUpdateDateView(UserPassesTestMixin, UpdateView):
    model = Match
    template_name = 'tournament/form.html'
    fields = ['match_date']

    def test_func(self):
        match = self.get_object()
        return self.request.user == match.tournament.tournament_admin

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.object.id})


class MatchUpdateScorersView(UserPassesTestMixin, CreateView):
    model = Scorers
    template_name = 'tournament/form.html'
    fields = ['scorer', 'minute']

    def test_func(self):
        match = Match.objects.get(id=self.kwargs['pk'])
        return self.request.user == match.tournament.tournament_admin

    def form_valid(self, form):
        form.instance.match = Match.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.kwargs['pk']})


class MatchDeleteScorersView(UserPassesTestMixin, DeleteView):
    model = Scorers

    def test_func(self):
        scorer = self.get_object()
        return self.request.user == scorer.match.tournament.tournament_admin

    def get_success_url(self):
        scorer = self.get_object()
        return reverse_lazy('tournament:match_detail', kwargs={'pk': scorer.match.id})


def is_power_of_two(teams):
    return math.log2(teams).is_integer()


def create_group_stages(num_groups, tournament):
    groups = []
    for i in range(1, num_groups + 1):
        group_name = f'Grupa {chr(97+i-1)}'
        group_stage = GroupStage.objects.create(name=group_name, order=i, tournament=tournament)
        groups.append(group_stage)
    return groups


def add_teams_to_groups(groups, teams):
    for group in groups:
        group_teams = teams[:4]
        group.teams.add(*group_teams)
        teams = teams[4:]
    return groups


def create_group_matches(group):
    teams = list(group.teams.all())
    matches = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            match = Match.objects.create(tournament=group.tournament, order=len(matches) + 1, phase=0,
                                         team1=teams[i], team2=teams[j], is_group=True)
            group.matches.add(match)
            matches.append(match)


def get_number_playoff_matches(num_teams):
    power_of_two = 1
    while power_of_two <= num_teams:
        power_of_two *= 2
    return power_of_two // 4


def create_playoff_matches(num_matches, tournament):
    matches = []
    num_matches = num_matches // 2
    phase = 1
    while num_matches != 1:
        for i in range(1, num_matches + 1):
            match = Match.objects.create(tournament=tournament, order=i, phase=phase)
            matches.append(match)
        num_matches //= 2
        phase += 1
    final_match = Match.objects.create(tournament=tournament, order=1, phase=phase)
    matches.append(final_match)
    mini_final = Match.objects.create(tournament=tournament, order=2, phase=phase)
    matches.append(mini_final)
    return matches


class TournamentCreateGroupsPlayoff(UserPassesTestMixin, View):
    def test_func(self):
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])
        return self.request.user == tournament.tournament_admin and not tournament.phases_drawn

    def get(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        teams = list(tournament.teams.all())
        total_teams = len(teams)

        if total_teams < 8:
            message = 'Aby rozpocząć turniej z fazą grupową musi byc przynajmniej 8 drużyn'
            return render(request,'tournament/message.html', {'message':message})

        if is_power_of_two(total_teams):
            number_playoff_matches = get_number_playoff_matches(total_teams)
            groups = create_group_stages(total_teams//4, tournament)
            random.shuffle(teams)
            groups = add_teams_to_groups(groups, teams)
            for group in groups:
                create_group_matches(group)
            playoff = Playoff.objects.create(tournament=tournament)
            playoff_matches = create_playoff_matches(number_playoff_matches, tournament)
            for match in playoff_matches:
                playoff.matches.add(match)
            tournament.phases_drawn = True
            tournament.save()
            return redirect('tournament:tournament_detail', pk)






