import pytest

from tournament.models import *
from accounts.models import *


@pytest.fixture
def user():
    u = CustomUser.objects.create(username='test_user')
    return u


@pytest.fixture
def user_not_creator():
    u = CustomUser.objects.create(username='test_user_two')
    return u


@pytest.fixture
def teams(user):
    lst = []
    for x in range(32):
        lst.append(Team.objects.create(name=x, short_name=x, captain=user))
    return lst


@pytest.fixture
def tournaments(user):
    lst = []
    for x in range(5):
        lst.append(Tournament.objects.create(name=x, max_teams_amount=x, tournament_admin=user))
    return lst