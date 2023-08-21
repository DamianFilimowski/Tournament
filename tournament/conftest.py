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
        team = Team.objects.create(name=x, short_name=x, captain=user)
        team.players.add(user)
        lst.append(team)
    return lst


@pytest.fixture
def tournaments(user):
    lst = []
    for x in range(5):
        lst.append(Tournament.objects.create(name=x, max_teams_amount=x+8, tournament_admin=user))
    return lst


@pytest.fixture
def matches(tournaments, teams):
    tournament = tournaments[0]
    team1 = teams[0]
    team2 = teams[1]
    lst = []
    for x in range(5):
        lst.append(Match.objects.create(tournament=tournament, order=x, phase=x,
                                        team1=team1, team2=team2, is_group=True))
    return lst


@pytest.fixture
def scorers(matches, user):
    match = matches[0]
    lst = []
    for x in range(5):
        lst.append(Scorers.objects.create(match=match, scorer=user, minute=x))
    return lst


@pytest.fixture
def groups(tournaments, matches):
    tournament = tournaments[0]
    lst = []
    for x in range(4):
        group_stage = GroupStage.objects.create(tournament=tournament, order=x, name=x)
        group_stage.matches.add(matches[x], matches[x+1])
        lst.append(group_stage)
    return lst


@pytest.fixture
def playoff(tournaments):
    tournament = tournaments[0]
    playoff = Playoff.objects.create(tournament=tournament)
    return playoff


@pytest.fixture
def users():
    lst = []
    for x in range(32):
        lst.append(CustomUser.objects.create(first_name=x, last_name=x, username=x))
    return lst
