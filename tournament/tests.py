import pytest
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client

from .models import *

browser = Client()


@pytest.mark.django_db
def test_team_list(teams):
    url = reverse('tournament:team_list')
    response = browser.get(url)
    assert response.status_code == 200
    assert list(response.context['object_list']) == teams


@pytest.mark.django_db
def test_team_detail(teams):
    team = teams[0]
    url = reverse('tournament:team_detail', kwargs={'pk': team.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == team


@pytest.mark.django_db
def test_team_create_logged(user):
    url = reverse('tournament:team_create')
    data = {
        'name': 'asd',
        'short_name': 'baba',
    }
    browser.force_login(user)
    response = browser.post(url, data)
    assert response.status_code == 302
    assert response.url.startswith(reverse('accounts:profile'))
    assert Team.objects.get(**data)


@pytest.mark.django_db
def test_team_create_logged_too_long_name_short(user):
    url = reverse('tournament:team_create')
    data = {
        'name': 'asd',
        'short_name': 'babasasasasa',
    }
    browser.force_login(user)
    response = browser.post(url, data)
    assert response.status_code == 200
    with pytest.raises(ObjectDoesNotExist):
        Team.objects.get(short_name='babasasasasa')


@pytest.mark.django_db
def test_team_create_not_logged():
    url = reverse('tournament:team_create')
    response = browser.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_team_update_captain_get(teams, user):
    team = teams[0]
    url = reverse('tournament:team_update', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_team_update_not_captain_get(teams, user_not_creator):
    team = teams[0]
    url = reverse('tournament:team_update', kwargs={'pk': team.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_team_update_captain_post(teams, user):
    team = teams[0]
    url = reverse('tournament:team_update', kwargs={'pk': team.id})
    browser.force_login(user)
    data = {
        'name': 'asdas',
        'short_name': 'blas'
    }
    response = browser.post(url, data)
    assert response.status_code == 302
    assert Team.objects.get(**data)
    assert response.url.startswith(reverse('tournament:team_detail', kwargs={'pk': team.id}))


@pytest.mark.django_db
def test_team_update_captain_post_too_long(teams, user):
    team = teams[0]
    url = reverse('tournament:team_update', kwargs={'pk': team.id})
    browser.force_login(user)
    data = {
        'name': 'asdas',
        'short_name': 'blassdsfsa'
    }
    response = browser.post(url, data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_team_delete_not_captain_get(teams, user_not_creator):
    team = teams[0]
    url = reverse('tournament:team_delete', kwargs={'pk': team.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_team_delete_captain_get(teams, user):
    team = teams[0]
    url = reverse('tournament:team_delete', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_team_delete_captain_post(teams, user):
    team = teams[0]
    url = reverse('tournament:team_delete', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.post(url)
    assert response.status_code == 302
    with pytest.raises(ObjectDoesNotExist):
        Team.objects.get(name=team.name, short_name=team.short_name, captain=team.captain)
    assert response.url.startswith(reverse('accounts:profile'))


@pytest.mark.django_db
def test_team_add_player_get(teams, user):
    team = teams[0]
    url = reverse('tournament:team_add_player', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_team_add_player_get_search(teams, user, users):
    team = teams[0]
    url = reverse('tournament:team_add_player', kwargs={'pk': team.id})
    data = {
        'imie': '1',
        'nazwisko': '1',
        'nazwa_uzytkownika': '1'
    }
    browser.force_login(user)
    response = browser.get(url, data)
    assert response.status_code == 200
    assert response.context['users'].get(username='1', first_name='1', last_name='1')
    assert response.context['users'].get(username='11', first_name='11', last_name='11')
    assert response.context['users'].get(username='21', first_name='21', last_name='21')


@pytest.mark.django_db
def test_team_add_player_get_not_captain(teams, user_not_creator):
    team = teams[0]
    url = reverse('tournament:team_add_player', kwargs={'pk': team.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_team_add_player_post(teams, user, users):
    team = teams[0]
    player = users[0]
    url = reverse('tournament:team_add_player', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.post(url, {'user_id': player.id})
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert team.players.get(username=player.username)
    assert any(f"Zaproszono użytkownika {player.username}" in message.message for message in messages)


@pytest.mark.django_db
def test_team_add_player_post_already_player(teams, user, users):
    team = teams[0]
    player = users[0]
    team.players.add(player)
    url = reverse('tournament:team_add_player', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.post(url, {'user_id': player.id})
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert any(f"Ten użytkownik już jest w Twojej drużynie" in message.message for message in messages)


@pytest.mark.django_db
def test_team_join_not_logged(teams):
    team = teams[0]
    url = reverse('tournament:team_join', kwargs={'pk': team.id})
    response = browser.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('accounts:login'))


@pytest.mark.django_db
def test_team_join(teams, users):
    team = teams[0]
    user = users[0]
    url = reverse('tournament:team_join', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert response.url.startswith(reverse('tournament:team_detail', kwargs={'pk': team.id}))
    assert any(f"Dołączyłeś do drużyny" in message.message for message in messages)
    assert team.players.filter(username=user.username, first_name=user.first_name, last_name=user.last_name)


@pytest.mark.django_db
def test_team_join_already_in_team(teams, users):
    team = teams[0]
    user = users[0]
    team.players.add(user)
    url = reverse('tournament:team_join', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_team_kick_player(teams, user, users):
    team = teams[0]
    player = users[0]
    team.players.add(player)
    url = reverse('tournament:team_kick', kwargs={'pk': team.id, 'player': player.id})
    browser.force_login(user)
    response = browser.get(url)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert not team.players.filter(username=player.username)
    assert any(f'Usunięto gracza {player.username}' in message.message for message in messages)


@pytest.mark.django_db
def test_team_kick_player_not_captain(teams, users):
    team = teams[0]
    player = users[0]
    team.players.add(player)
    url = reverse('tournament:team_kick', kwargs={'pk': team.id, 'player': player.id})
    browser.force_login(player)
    response = browser.get(url)
    assert response.status_code == 403
    assert team.players.filter(username=player.username)


@pytest.mark.django_db
def test_team_kick_player_does_not_exist(teams, user, users):
    team = teams[0]
    url = reverse('tournament:team_kick', kwargs={'pk': team.id, 'player': 99})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_team_kick_player_not_in_team(teams, user, users):
    team = teams[0]
    player = users[0]
    url = reverse('tournament:team_kick', kwargs={'pk': team.id, 'player': player.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_team_leave_captain(teams, user):
    team = teams[0]
    url = reverse('tournament:team_leave', kwargs={'pk': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403
    assert team.players.filter(id=user.id)


@pytest.mark.django_db
def test_team_leave(teams, users):
    team = teams[0]
    player = users[0]
    team.players.add(player)
    url = reverse('tournament:team_leave', kwargs={'pk': team.id})
    browser.force_login(player)
    response = browser.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('tournament:team_detail', kwargs={'pk': team.id}))
    assert not team.players.filter(id=player.id)


@pytest.mark.django_db
def test_team_leave_not_in_team(teams, users):
    team = teams[0]
    player = users[0]
    url = reverse('tournament:team_leave', kwargs={'pk': team.id})
    browser.force_login(player)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_list(tournaments):
    url = reverse('tournament:tournament_list')
    response = browser.get(url)
    assert response.status_code == 200
    assert list(response.context['object_list']) == tournaments


@pytest.mark.django_db
def test_tournament_create(user):
    browser.force_login(user)
    url = reverse('tournament:tournament_create')
    name = 'test_tournament'
    max_teams = 16
    data = {
        'name': name,
        'max_teams_amount': max_teams
    }
    response = browser.post(url, data)
    assert response.status_code == 302
    assert Tournament.objects.get(name=name, max_teams_amount=max_teams)
    assert response.url.startswith(reverse('tournament:tournament_list'))


@pytest.mark.django_db
def test_tournament_create_not_enough_teams(user):
    browser.force_login(user)
    url = reverse('tournament:tournament_create')
    name = 'test_tournament'
    max_teams = 7
    data = {
        'name': name,
        'max_teams_amount': max_teams
    }
    response = browser.post(url, data)
    assert response.status_code == 200
    with pytest.raises(ObjectDoesNotExist):
        Tournament.objects.get(name=name, max_teams_amount=max_teams)


@pytest.mark.django_db
def test_tournament_create_not_logged():
    url = reverse('tournament:tournament_create')
    response = browser.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('accounts:login'))


@pytest.mark.django_db
def test_tournament_detail(tournaments):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_detail', kwargs={'pk': tournament.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == tournament


@pytest.mark.django_db
def test_tournament_update_creator_get(tournaments, user):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_update', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_tournament_update_not_creator_get(tournaments, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_update', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_update_creator_post(tournaments, user):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_update', kwargs={'pk': tournament.id})
    browser.force_login(user)
    data = {
        'name': 'asdas',
        'max_teams_amount': 9
    }
    response = browser.post(url, data)
    assert response.status_code == 302
    assert Tournament.objects.get(**data)
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_delete_not_creator_get(tournaments, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_delete', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_delete_creator_get(tournaments, user):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_delete', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_tournament_delete_creator_post(tournaments, user):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_delete', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.post(url)
    assert response.status_code == 302
    with pytest.raises(ObjectDoesNotExist):
        Tournament.objects.get(name=tournament.name, max_teams_amount=tournament.max_teams_amount,
                               tournament_admin=tournament.tournament_admin)
    assert response.url.startswith(reverse('accounts:profile'))


@pytest.mark.django_db
def test_tournament_add_team(tournaments, teams, user):
    tournament = tournaments[0]
    team = teams[0]
    url = reverse('tournament:tournament_add_team', kwargs={'pk': tournament.id})
    browser.force_login(user)
    data = {'id': team.id}
    response = browser.post(url, data)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert tournament.teams.filter(id=team.id)
    assert any(f"Drużyna {team.name} została dodana" in message.message for message in messages)


@pytest.mark.django_db
def test_tournament_add_team_already_in_tournament(tournaments, teams, user):
    tournament = tournaments[0]
    team = teams[0]
    tournament.teams.add(team)
    url = reverse('tournament:tournament_add_team', kwargs={'pk': tournament.id})
    browser.force_login(user)
    data = {'id': team.id}
    response = browser.post(url, data)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert any(f'Ta drużyna jest juz w tym turnieju' in message.message for message in messages)


@pytest.mark.django_db
def test_tournament_add_team_player_already_in_tournament(tournaments, teams, user):
    tournament = tournaments[0]
    team = teams[0]
    tournament.teams.add(team)
    team2 = teams[1]
    url = reverse('tournament:tournament_add_team', kwargs={'pk': tournament.id})
    browser.force_login(user)
    data = {'id': team2.id}
    response = browser.post(url, data)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert any(f'Zawodnik drużyny {team2.name} juz gra w tym turnieju' in message.message for message in messages)
    assert not tournament.teams.filter(id=team2.id)


@pytest.mark.django_db
def test_tournament_add_team_last_one(tournaments, teams, user):
    tournament = tournaments[0]
    for i in range(1, 8):
        team = teams[i]
        team.players.remove(user)
        tournament.teams.add(team)
    tournament.max_teams_amount = 8
    tournament.save()
    url = reverse('tournament:tournament_add_team', kwargs={'pk': tournament.id})
    browser.force_login(user)
    team = teams[0]
    data = {'id': team.id}
    response = browser.post(url, data)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert any(f"Osiągnięto maksymalną ilość drużyn" in message.message for message in messages)
    assert tournament.teams.filter(id=team.id)


@pytest.mark.django_db
def test_tournament_add_team_over_max(tournaments, teams, user):
    tournament = tournaments[0]
    for i in range(1, 9):
        team = teams[i]
        team.players.remove(user)
        tournament.teams.add(team)
    tournament.max_teams_amount = 8
    tournament.save()
    url = reverse('tournament:tournament_add_team', kwargs={'pk': tournament.id})
    browser.force_login(user)
    team = teams[0]
    data = {'id': team.id}
    response = browser.post(url, data)
    assert response.status_code == 403
    assert not tournament.teams.filter(id=team.id)


@pytest.mark.django_db
def test_tournament_kick_team(user, tournaments, teams):
    tournament = tournaments[0]
    team = teams[0]
    tournament.teams.add(team)
    url = reverse('tournament:tournament_kick_team', kwargs={'pk': tournament.id, 'team': team.id})
    browser.force_login(user)
    response = browser.get(url)
    messages = get_messages(response.wsgi_request)
    assert response.status_code == 302
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk':tournament.id}))
    assert not tournament.teams.filter(id=team.id)
    assert any(f"Druzyna {team.name} została usunięta z turnieju" in message.message for message in messages)


@pytest.mark.django_db
def test_tournament_kick_team_not_admin(user_not_creator, tournaments, teams):
    tournament = tournaments[0]
    team = teams[0]
    tournament.teams.add(team)
    url = reverse('tournament:tournament_kick_team', kwargs={'pk': tournament.id, 'team': team.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403
    assert tournament.teams.filter(id=team.id)


@pytest.mark.django_db
def test_tournament_kick_team_not_in_tournament(user, tournaments, teams):
    tournament = tournaments[0]
    team = teams[0]
    url = reverse('tournament:tournament_kick_team', kwargs={'pk': tournament.id, 'team': team.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_kick_team_doesnt_exist(user, tournaments, teams):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_kick_team', kwargs={'pk': tournament.id, 'team': 555})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_match_detail(matches, groups):
    match = matches[0]
    url = reverse('tournament:match_detail', kwargs={'pk': match.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == match


@pytest.mark.django_db
def test_match_update_result_not_creator(matches, user_not_creator):
    match = matches[0]
    url = reverse('tournament:match_update_result', kwargs={'pk': match.id})
    browser.force_login(user_not_creator)
    data = {
        'team1_score': 1,
        'team2_score': 2
    }
    response = browser.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_match_update_result_creator(matches, user, groups):
    group_stage = groups[0]
    match = matches[0]
    url = reverse('tournament:match_update_result', kwargs={'pk': match.id})
    browser.force_login(user)
    data = {
        'team1_score': 1,
        'team2_score': 2
    }
    response = browser.post(url, data)
    assert response.status_code == 302
    match = Match.objects.get(id=match.id)
    assert match.result == 2
    assert match in group_stage.matches_finished.all()
    assert response.url.startswith(reverse('tournament:match_detail', kwargs={'pk': match.id}))


@pytest.mark.django_db
def test_match_update_date_not_creator(matches, user_not_creator):
    match = matches[0]
    url = reverse('tournament:match_update_date', kwargs={'pk': match.id})
    browser.force_login(user_not_creator)
    data = {
        'match_date': '2023-05-22 20:00:00'
    }
    response = browser.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_match_update_date_creator(matches, user):
    match = matches[0]
    url = reverse('tournament:match_update_date', kwargs={'pk': match.id})
    browser.force_login(user)
    data = {
        'match_date': '2023-05-22 20:00:00'
    }
    response = browser.post(url, data)
    assert response.status_code == 302
    assert Match.objects.get(**data)
    assert response.url.startswith(reverse('tournament:match_detail', kwargs={'pk': match.id}))


@pytest.mark.django_db
def test_match_update_scorers_not_creator(matches, user_not_creator):
    match = matches[0]
    url = reverse('tournament:match_update_scorers', kwargs={'pk': match.id})
    browser.force_login(user_not_creator)
    data = {
        'scorer': user_not_creator.id,
        'minute': 5
    }
    response = browser.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_match_update_scorers_creator(matches, user):
    match = matches[0]
    url = reverse('tournament:match_update_scorers', kwargs={'pk': match.id})
    browser.force_login(user)
    match.team2.players.remove(user)
    data = {
        'scorer': user.id,
        'minute': 5
    }
    response = browser.post(url, data)
    user = CustomUser.objects.get(id=user.id)
    assert response.status_code == 302
    assert Scorers.objects.get(**data)
    assert user.goals == 1
    assert response.url.startswith(reverse('tournament:match_detail', kwargs={'pk': match.id}))


@pytest.mark.django_db
def test_scorers_delete_not_creator(scorers, user_not_creator):
    scorer = scorers[0]
    url = reverse('tournament:match_delete_scorers', kwargs={'pk': scorer.id})
    browser.force_login(user_not_creator)
    response = browser.post(url)
    assert response.status_code == 403
    assert Scorers.objects.get(match=scorer.match, scorer=scorer.scorer, minute=scorer.minute)


@pytest.mark.django_db
def test_scorers_delete_creator(scorers, user):
    scorer = scorers[0]
    url = reverse('tournament:match_delete_scorers', kwargs={'pk': scorer.id})
    browser.force_login(user)
    response = browser.post(url)
    user = CustomUser.objects.get(id=user.id)
    assert user.goals == -1
    assert response.status_code == 302
    with pytest.raises(ObjectDoesNotExist):
        Scorers.objects.get(match=scorer.match, scorer=scorer.scorer, minute=scorer.minute)
    assert response.url.startswith(reverse('tournament:match_detail', kwargs={'pk': scorer.match.id}))


@pytest.mark.django_db
def test_tournament_create_groups_playoff_not_creator(tournaments, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_create_groups_playoff_phases_drawn(tournaments, user):
    tournament = tournaments[0]
    tournament.phases_drawn = True
    tournament.save()
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_create_groups_playoff_seven_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:7])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 200
    with pytest.raises(ObjectDoesNotExist):
        Playoff.objects.get(tournament=tournament)
    assert response.context['message'] == 'Aby rozpocząć turniej z fazą grupową musi byc przynajmniej 8 drużyn'


@pytest.mark.django_db
def test_tournament_create_groups_playoff_eight_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:8])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    group1 = tournament.groupstage_set.get(order=1, name='Grupa a')
    group2 = tournament.groupstage_set.get(order=2, name='Grupa b')
    match = tournament.playoff.matches.get(phase=1, order=1)
    assert match.phase_name == 'Półfinał'
    assert group1.teams.count() == 4
    assert group1.matches.count() == 6
    assert group2.teams.count() == 4
    assert group2.matches.count() == 6
    assert response.status_code == 302
    assert tournament.groupstage_set.count() == 2
    assert tournament.match_set.count() == 16
    assert tournament.playoff.matches.count() == 4
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_create_groups_playoff_eleven_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:11])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    group1 = tournament.groupstage_set.get(order=1, name='Grupa a')
    group2 = tournament.groupstage_set.get(order=2, name='Grupa b')
    match = tournament.playoff.matches.get(phase=1, order=1)
    assert match.phase_name == 'Półfinał'
    assert group1.teams.count() == 6
    assert group1.matches.count() == 15
    assert group2.teams.count() == 5
    assert group2.matches.count() == 10
    assert response.status_code == 302
    assert tournament.groupstage_set.count() == 2
    assert tournament.match_set.count() == 29
    assert tournament.playoff.matches.count() == 4
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_create_groups_playoff_eighteen_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:18])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_groups_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    group1 = tournament.groupstage_set.get(order=1, name='Grupa a')
    group2 = tournament.groupstage_set.get(order=4, name='Grupa d')
    match = tournament.playoff.matches.get(phase=1, order=1)
    assert match.phase_name == 'Ćwierćfinał'
    assert group1.teams.count() == 5
    assert group1.matches.count() == 10
    assert group2.teams.count() == 4
    assert group2.matches.count() == 6
    assert response.status_code == 302
    assert tournament.groupstage_set.count() == 4
    assert tournament.match_set.count() == 40
    assert tournament.playoff.matches.count() == 8
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_create_playoff_not_creator(tournaments, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_create_playoff_phases_drawn(tournaments, user):
    tournament = tournaments[0]
    tournament.phases_drawn = True
    tournament.save()
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_create_playoff_seven_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:7])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    with pytest.raises(ObjectDoesNotExist):
        Playoff.objects.get(tournament=tournament)
    assert response.status_code == 200
    assert response.context['message'] == 'Aby rozpocząć turniej musi byc przynajmniej 8 drużyn'


@pytest.mark.django_db
def test_tournament_create_playoff_eight_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:8])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    match = tournament.playoff.matches.get(phase=1, order=1)
    assert match.phase_name == 'Ćwierćfinał'
    assert response.status_code == 302
    assert tournament.playoff.matches.count() == 8
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


def check_number_auto_promoted_teams(playoff):
    matches = playoff.matches.filter(phase=1)
    qty = 0
    for match in matches:
        if match.team2 is None:
            qty += 1
    return qty


def check_if_teams_promoted_correctly(playoff):
    matches = playoff.matches.filter(phase=2)
    qty = matches.count() * 2
    for match in matches:
        if match.team1 is None:
            qty -= 1
        if match.team2 is None:
            qty -= 1
    return qty


@pytest.mark.django_db
def test_tournament_create_playoff_eleven_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:11])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    match = tournament.playoff.matches.get(phase=1, order=1)
    playoff = Playoff.objects.get(tournament=tournament)
    assert check_number_auto_promoted_teams(playoff) == 5
    assert check_if_teams_promoted_correctly(playoff) == 5
    assert match.phase_name == '1/8 finału'
    assert response.status_code == 302
    assert tournament.playoff.matches.count() == 16
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_create_playoff_eighteen_teams(tournaments, teams, user):
    tournament = tournaments[0]
    teams = list(teams[:18])
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    match = tournament.playoff.matches.get(phase=1, order=1)
    playoff = Playoff.objects.get(tournament=tournament)
    assert check_number_auto_promoted_teams(playoff) == 14
    assert check_if_teams_promoted_correctly(playoff) == 14
    assert match.phase_name == '1/16 finału'
    assert response.status_code == 302
    assert tournament.playoff.matches.count() == 32
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_group_stage_detail(groups):
    group = groups[0]
    url = reverse('tournament:groupstage_detail', kwargs={'pk': group.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == group


@pytest.mark.django_db
def test_playoff_detail(playoff):
    url = reverse('tournament:playoff_detail', kwargs={'pk': playoff.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == playoff


@pytest.mark.django_db
def test_playoff_detail_not_exist():
    url = reverse('tournament:playoff_detail', kwargs={'pk': 1})
    response = browser.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_tournament_start(tournaments):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_start', kwargs={'pk': tournament.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['pk'] == tournament.id


@pytest.mark.django_db
def test_tournament_create_playoff_creator(tournaments, teams, user):
    tournament = tournaments[0]
    teams = teams[:14]
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    playoff = Playoff.objects.get(tournament=tournament)
    playoff_none_team1 = playoff.matches.filter(team1=None, phase=1)
    playoff_none_team2 = playoff.matches.filter(team2=None, phase=1)
    playoff_next_phase = playoff.matches.filter(phase=2)
    have_t1 = playoff_next_phase.filter(team1__isnull=False)
    have_t2 = playoff_next_phase.filter(team2__isnull=False)
    assert len(have_t1) + len(have_t2) == 2
    assert len(playoff_none_team1) == 0
    assert len(playoff_none_team2) == 2
    assert response.status_code == 302
    assert response.url.startswith(reverse('tournament:tournament_detail', kwargs={'pk': tournament.id}))


@pytest.mark.django_db
def test_tournament_create_playoff_not_creator(tournaments, teams, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_create_playoff', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_join_not_captain(tournaments, user_not_creator):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_join', kwargs={'pk': tournament.id})
    browser.force_login(user_not_creator)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_join_max_teams(tournaments, teams, user):
    tournament = tournaments[0]
    tournament.max_teams_amount = 9
    teams = teams[:9]
    tournament.teams.add(*teams)
    url = reverse('tournament:tournament_join', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_tournament_join_phases_drawn(tournaments, user):
    tournament = tournaments[0]
    tournament.phases_drawn = True
    url = reverse('tournament:tournament_join', kwargs={'pk': tournament.id})
    browser.force_login(user)
    response = browser.get(url)
    assert response.status_code == 403
