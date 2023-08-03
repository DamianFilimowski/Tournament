import math

from tournament.models import *


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
