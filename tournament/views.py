import random

from django.db.models import Max
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View

from .utils import *


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
        response = super().form_valid(form)
        set_result(self)
        if self.object.is_group:
            group_stage = GroupStage.objects.get(matches=self.object)
            from_matches_to_finished(self, group_stage)
            if not group_stage.matches.all():
                finished_matches = group_stage.matches_finished.all()
                group_data = get_group_data(finished_matches)
                team1 = group_data[0][0]
                team2 = group_data[1][0]
                group_stage.promoted_teams.add(team1, team2)
                order = group_stage.order
                playoff = Playoff.objects.get(tournament=group_stage.tournament)
                matches = playoff.matches.filter(phase=1)
                if order % 2 == 0:
                    match1 = matches.get(order=order - 1)
                    match2 = matches.get(order=order)
                    match1.team2 = team2
                    match1.save()
                    match2.team1 = team1
                    match2.save()
                else:
                    match1 = matches.get(order=order)
                    match2 = matches.get(order=order + 1)
                    match1.team1 = team1
                    match1.save()
                    match2.team2 = team2
                    match2.save()
        else:
            playoff = Playoff.objects.get(tournament=self.object.tournament)
            max_phase = playoff.matches.aggregate(Max('phase'))['phase__max']
            if self.object.team1_score > self.object.team2_score:
                winner = self.object.team1
                loser = self.object.team2
            else:
                winner = self.object.team2
                loser = self.object.team1
            if self.object.phase == max_phase - 1:
                matches = playoff.matches.filter(phase=max_phase)
                final = matches.get(order=1)
                mini_final = matches.get(order=2)
                if self.object.order == 1:
                    final.team1 = winner
                    final.save()
                    mini_final.team1 = loser
                    mini_final.save()
                else:
                    final.team2 = winner
                    final.save()
                    mini_final.team2 = loser
                    mini_final.save()
            else:
                matches = playoff.matches.filter(phase=self.object.phase + 1)
                if self.object.order % 2 == 0:
                    match = matches.get(order=self.object.order // 2)
                    match.team2 = winner
                    match.save()
                else:
                    match = matches.get(order=(self.object.order + 1) // 2)
                    match.team1 = winner
                    match.save()
        return response

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
            return render(request, 'tournament/message.html', {'message': message})

        elif is_power_of_two(total_teams):
            number_playoff_matches = get_number_playoff_matches(total_teams)
            groups = create_group_stages(total_teams // 4, tournament)
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


class GroupStageDetailView(DetailView):
    model = GroupStage
    template_name = 'tournament/groupstage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_stage = self.object
        matches = group_stage.matches_finished.all()
        group_data = get_group_data(matches)
        context['group_data'] = group_data
        return context


class PlayoffDetailView(DetailView):
    model = Playoff
    template_name = 'tournament/playoff_detail.html'


class TournamentStart(View):
    def test_func(self):
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])
        return self.request.user == tournament.tournament_admin and not tournament.phases_drawn

    def get(self, request, pk):
        return render(request, 'tournament/tournament_start.html', {'pk': pk})

