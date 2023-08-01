import pytest
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
def test_tournament_list(tournaments):
    url = reverse('tournament:tournament_list')
    response = browser.get(url)
    assert response.status_code == 200
    assert list(response.context['object_list']) == tournaments


@pytest.mark.django_db
def test_tournament_detail(tournaments):
    tournament = tournaments[0]
    url = reverse('tournament:tournament_detail', kwargs={'pk': tournament.id})
    response = browser.get(url)
    assert response.status_code == 200
    assert response.context['object'] == tournament


@pytest.mark.django_db
def test_tournament_create_logged(user):
    url = reverse('tournament:tournament_create')
    data = {
        'name': 'asd',
        'max_teams_amount': 5,
    }
    browser.force_login(user)
    response = browser.post(url, data)
    assert response.status_code == 302
    assert response.url.startswith(reverse('tournament:tournament_list'))
    assert Tournament.objects.get(**data)


@pytest.mark.django_db
def test_tournament_create_not_logged():
    url = reverse('tournament:tournament_create')
    response = browser.get(url)
    assert response.status_code == 302


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
        'max_teams_amount': 4
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
