import random
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View

from .forms import *
from .utils import *


# Create your views here.

class TeamListView(ListView):
    model = Team
    template_name = 'tournament/team_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('nazwa', '')
        short_name = self.request.GET.get('krotka_nazwa', '')
        queryset = queryset.filter(name__icontains=name, short_name__icontains=short_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchTeamForm(self.request.GET)
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'tournament/form.html'
    fields = ['name', 'short_name']
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        form.instance.captain = self.request.user
        response = super().form_valid(form)
        self.object.players.add(self.request.user)

        return response


class TeamDetailView(DetailView):
    model = Team
    template_name = 'tournament/team_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages_received = messages.get_messages(self.request)
        message_list = list(messages_received)
        context['message_list'] = message_list
        return context


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


class TeamAddPlayer(UserPassesTestMixin, View):
    def test_func(self):
        team = Team.objects.get(pk=self.kwargs['pk'])
        return self.request.user == team.captain

    def get(self, request, pk):
        search_form = SearchPersonForm(request.GET)
        users = CustomUser.objects.all()
        if search_form.is_valid():
            first_name = search_form.cleaned_data.get('imie', '')
            last_name = search_form.cleaned_data.get('nazwisko', '')
            username = search_form.cleaned_data.get('nazwa_uzytkownika', '')
            users = users.filter(first_name__icontains=first_name, last_name__icontains=last_name,
                                 username__icontains=username)
        messages_received = messages.get_messages(request)
        message_list = list(messages_received)
        context = {'search_form': search_form, 'users': users, 'message_list': message_list, 'pk': pk}
        return render(request, 'tournament/team_add_player.html', context=context)

    def post(self, request, pk):
        team = Team.objects.get(pk=self.kwargs['pk'])
        player = request.POST.get('user_id')
        player = CustomUser.objects.get(id=player)
        team_players = team.players.all()
        if player in team_players:
            messages.success(request, "Ten użytkownik już jest w Twojej drużynie")
            return redirect('tournament:team_add_player', pk)
        team.players.add(player)
        messages.success(request, f"Zaproszono użytkownika {player.username}")
        return redirect('tournament:team_add_player', pk)


class TeamJoinView(UserPassesTestMixin, View):
    def test_func(self):
        team = Team.objects.get(pk=self.kwargs['pk'])
        return self.request.user != team.players and self.request.user.is_authenticated

    def get(self, request, pk):
        user = self.request.user
        team = Team.objects.get(pk=pk)
        team.players.add(user)
        messages.success(request, "Dołączyłeś do drużyny")
        return redirect('tournament:team_detail', pk)


class TeamKickPlayerView(UserPassesTestMixin, View):
    def test_func(self):
        team = Team.objects.get(pk=self.kwargs['pk'])
        return self.request.user == team.captain

    def get(self, request, pk, player):
        team = Team.objects.get(pk=pk)
        player = CustomUser.objects.get(pk=player)
        team.players.remove(player)
        messages.success(request, f"Usunięto gracza {player.username}")
        return redirect('tournament:team_detail', pk)


class TeamLeaveView(UserPassesTestMixin, View):
    def test_func(self):
        team = Team.objects.get(pk=self.kwargs['pk'])
        return self.request.user in team.players.all() and self.request.user != team.captain

    def get(self, request, pk):
        user = self.request.user
        team = Team.objects.get(pk=pk)
        team.players.remove(user)
        messages.success(request, "Opuściłeś drużynę")
        return redirect('tournament:team_detail', pk)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages_received = messages.get_messages(self.request)
        message_list = list(messages_received)
        context['message_list'] = message_list
        return context


class TournamentUpdateView(UserPassesTestMixin, UpdateView):
    model = Tournament
    template_name = 'tournament/form.html'
    fields = ['name', 'max_teams_amount']

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


class TournamentAddTeamView(UserPassesTestMixin, View):
    def test_func(self):
        tournament = Tournament.objects.get(id=self.kwargs['pk'])
        teams = list(tournament.teams.all())
        max_teams = tournament.max_teams_amount
        return self.request.user == tournament.tournament_admin and len(teams) < max_teams

    def get(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        tournament_teams = tournament.teams.all()
        teams = Team.objects.all().exclude(pk__in=tournament_teams)
        form = SearchTeamForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('nazwa', '')
            short_name = form.cleaned_data.get('krotka_nazwa', '')
            teams = teams.filter(name__icontains=name, short_name__icontains=short_name)
        messages_received = messages.get_messages(request)
        message_list = list(messages_received)
        context = {'teams': teams, 'form': form, 'tournament': tournament, 'message_list': message_list}
        return render(request, 'tournament/tournament_add_team.html', context=context)

    def post(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        team = request.POST.get('id')
        team = Team.objects.get(id=team)
        tournament_teams = tournament.teams.all()
        if team in tournament_teams:
            messages.success(request, "Ta drużyna jest juz w tym turnieju")
            return redirect('tournament:tournament_add_team', pk)
        if if_player_in_tournament(tournament, team):
            messages.success(request, f"Zawodnik drużyny '{team.name}' juz gra w tym turnieju")
            return redirect('tournament:tournament_add_team', pk)
        tournament.teams.add(team)
        tournament_teams = len(list(tournament.teams.all()))
        if tournament_teams == tournament.max_teams_amount:
            messages.success(request, f"Osiągnięto maksymalną ilość drużyn")
            return redirect('tournament:tournament_detail', pk)
        messages.success(request, f"Drużyna {team.name} została dodana")
        return redirect('tournament:tournament_add_team', pk)


class TournamentKickTeamView(UserPassesTestMixin, View):
    def test_func(self):
        tournament = Tournament.objects.get(id=self.kwargs['pk'])
        return self.request.user == tournament.tournament_admin

    def get(self, request, pk, team):
        tournament = Tournament.objects.get(id=pk)
        team = Team.objects.get(id=team)
        tournament.teams.remove(team)
        messages.success(request, f"Druzyna {team.name} została usunięta z turnieju")
        return redirect('tournament:tournament_detail', pk)




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
            if self.object.team1_score == self.object.team2_score:
                return response
            elif self.object.team1_score > self.object.team2_score:
                winner = self.object.team1
                loser = self.object.team2
            else:
                winner = self.object.team2
                loser = self.object.team1
            if self.object.phase == max_phase - 1:
                set_teams_for_final_phase(self, max_phase, playoff, winner, loser)
            elif self.object.phase == max_phase:
                return response
            else:
                move_to_next_phase(self, playoff, winner)
        return response

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.object.id})


class MatchUpdateExtraTimeView(UserPassesTestMixin, UpdateView):
    model = Match
    template_name = 'tournament/form.html'
    fields = ['team1_extra_time_score', 'team2_extra_time_score']

    def test_func(self):
        match = self.get_object()
        return (self.request.user == match.tournament.tournament_admin and match.team1_score == match.team2_score
                and match.team1_score and match.team1_extra_time_score is None)

    def form_valid(self, form):
        response = super().form_valid(form)
        playoff = Playoff.objects.get(tournament=self.object.tournament)
        max_phase = playoff.matches.aggregate(Max('phase'))['phase__max']
        if self.object.team1_extra_time_score == self.object.team2_extra_time_score:
            return response
        elif self.object.team1_extra_time_score > self.object.team2_extra_time_score:
            winner = self.object.team1
            loser = self.object.team2
        else:
            winner = self.object.team2
            loser = self.object.team1
        if self.object.phase == max_phase - 1:
            set_teams_for_final_phase(self, max_phase, playoff, winner, loser)
        elif self.object.phase == max_phase:
            return response
        else:
            move_to_next_phase(self, playoff, winner)
        return response

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.object.id})


class MatchUpdatePenaltyView(UserPassesTestMixin, UpdateView):
    model = Match
    template_name = 'tournament/form.html'
    fields = ['team1_penalty_score', 'team2_penalty_score']

    def test_func(self):
        match = self.get_object()
        return (self.request.user == match.tournament.tournament_admin and match.team1_score == match.team2_score
                and match.team1_score and match.team1_extra_time_score is not None and match.team1_penalty_score is None)

    def form_valid(self, form):
        response = super().form_valid(form)
        playoff = Playoff.objects.get(tournament=self.object.tournament)
        max_phase = playoff.matches.aggregate(Max('phase'))['phase__max']
        if self.object.team1_penalty_score == self.object.team2_penalty_score:
            return response
        elif self.object.team1_penalty_score > self.object.team2_penalty_score:
            winner = self.object.team1
            loser = self.object.team2
        else:
            winner = self.object.team2
            loser = self.object.team1
        if self.object.phase == max_phase - 1:
            set_teams_for_final_phase(self, max_phase, playoff, winner, loser)
        elif self.object.phase == max_phase:
            return response
        else:
            move_to_next_phase(self, playoff, winner)
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
        response = super().form_valid(form)
        scorer = form.instance.scorer
        user = CustomUser.objects.get(id=scorer.id)
        user.goals += 1
        user.save()
        return response

    def get_success_url(self):
        return reverse_lazy('tournament:match_detail', kwargs={'pk': self.kwargs['pk']})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        match = Match.objects.get(id=self.kwargs['pk'])
        form.fields['scorer'].queryset = match.team1.players.all() | match.team2.players.all()
        return form


class MatchDeleteScorersView(UserPassesTestMixin, DeleteView):
    model = Scorers

    def test_func(self):
        scorer = self.get_object()
        return self.request.user == scorer.match.tournament.tournament_admin

    def get_success_url(self):
        scorer = self.get_object()
        return reverse_lazy('tournament:match_detail', kwargs={'pk': scorer.match.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        scorer = self.object.scorer
        user = CustomUser.objects.get(id=scorer.id)
        user.goals -= 1
        user.save()
        return response


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
            groups = create_group_stages(number_playoff_matches // 2, tournament)
            random.shuffle(teams)
            groups = add_teams_to_groups(groups, teams)
            for group in groups:
                create_group_matches(group)
            playoff = Playoff.objects.create(tournament=tournament)
            playoff_matches = create_playoff_matches(number_playoff_matches, tournament)
            for match in playoff_matches:
                playoff.matches.add(match)
            set_phase_names(playoff)
            tournament.phases_drawn = True
            tournament.save()
            return redirect('tournament:tournament_detail', pk)

        else:
            number_playoff_matches = get_number_playoff_matches(total_teams)
            groups = create_group_stages(number_playoff_matches//2, tournament)
            random.shuffle(teams)
            groups = add_teams_to_groups(groups, teams)
            list_groups = list(groups)
            for i, team in enumerate(teams):
                group_index = i % len(list_groups)
                groups[group_index].teams.add(team)
            for group in groups:
                create_group_matches(group)
            playoff = Playoff.objects.create(tournament=tournament)
            playoff_matches = create_playoff_matches(number_playoff_matches, tournament)
            for match in playoff_matches:
                playoff.matches.add(match)
            set_phase_names(playoff)
            tournament.phases_drawn = True
            tournament.save()
            return redirect('tournament:tournament_detail', pk)


class TournamentCreatePlayoff(UserPassesTestMixin, View):
    def test_func(self):
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])
        return self.request.user == tournament.tournament_admin and not tournament.phases_drawn

    def get(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        teams = list(tournament.teams.all())
        total_teams = len(teams)
        if is_power_of_two(total_teams):
            num_matches = get_number_playoff_matches(total_teams) * 2
        else:
            num_matches = get_number_playoff_matches(total_teams) * 4
        matches = create_playoff_matches(num_matches, tournament)
        random.shuffle(teams)
        playoff = Playoff.objects.create(tournament=tournament)
        for match in matches:
            playoff.matches.add(match)
        set_phase_names(playoff)
        matches = playoff.matches.filter(phase=1)
        for match in matches:
            team1 = teams.pop(0)
            match.team1 = team1
            match.save()
        matches = list(matches)
        random.shuffle(matches)
        for i in range(0, len(teams)):
            team2 = teams.pop(0)
            matches[i].team2 = team2
            matches[i].save()
        matches = playoff.matches.filter(team2=None, phase=1)
        playoff_matches = playoff.matches.filter(phase=2)
        for match in matches:
            if match.order % 2 == 0:
                match_playoff = playoff_matches.get(order=match.order // 2)
                match_playoff.team2 = match.team1
                match_playoff.save()
            else:
                match_playoff = playoff_matches.get(order=(match.order + 1) // 2)
                match_playoff.team1 = match.team1
                match_playoff.save()
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


class TournamentJoin(UserPassesTestMixin, View):
    def test_func(self):
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])
        max_teams = tournament.max_teams_amount
        teams_number = tournament.teams.count()
        is_captain = Team.objects.filter(captain=self.request.user).exclude(tournament=tournament)
        return len(is_captain) > 0 and not tournament.phases_drawn and max_teams > teams_number

    def get(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        teams = Team.objects.filter(captain=self.request.user).exclude(tournament=tournament)
        messages_received = messages.get_messages(request)
        message_list = list(messages_received)
        return render(request, 'tournament/tournament_join.html', {'teams': teams,
                                                                   'tournament': tournament, 'message_list': message_list})

    def post(self, request, pk):
        team = Team.objects.get(id=request.POST.get('team_id'))
        tournament = Tournament.objects.get(pk=pk)
        if if_player_in_tournament(tournament, team):
            messages.success(request, "Jeden z Twoich zawodników jest członkiem innej drużyny będącej w turnieju")
            return redirect('tournament:tournament_join', pk)
        tournament.teams.add(team)
        return redirect('tournament:tournament_detail', pk)


class TournamentScorersView(View):
    def get(self, request, pk):
        scorers = CustomUser.objects.filter(scorers__match__tournament=pk).annotate(scored=Count('scorers')).order_by('-scored')
        return render(request, 'tournament/top_scorers.html', {'scorers': scorers, 'pk': pk})

