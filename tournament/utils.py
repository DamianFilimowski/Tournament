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


def get_group_data(matches):
    group_data = {}

    for match in matches:
        if match.team1 not in group_data:
            group_data[match.team1] = {
                'points': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'goal_difference': 0
            }
        if match.team2 not in group_data:
            group_data[match.team2] = {
                'points': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'goal_difference': 0
            }
        if match.team1_score > match.team2_score:
            group_data[match.team1]['points'] += 3
        elif match.team1_score < match.team2_score:
            group_data[match.team2]['points'] += 3
        else:
            group_data[match.team1]['points'] += 1
            group_data[match.team2]['points'] += 1

        group_data[match.team1]['goals_scored'] += match.team1_score
        group_data[match.team1]['goals_conceded'] += match.team2_score
        group_data[match.team1]['goal_difference'] += match.team1_score - match.team2_score

        group_data[match.team2]['goals_scored'] += match.team2_score
        group_data[match.team2]['goals_conceded'] += match.team1_score
        group_data[match.team2]['goal_difference'] += match.team2_score - match.team1_score
    group_data = group_data.items()
    group_data = sorted(group_data, key=lambda item: -item[1]['points'])
    return group_data


def set_result(self):
    if self.object.team1_score > self.object.team2_score:
        self.object.result = 1
    elif self.object.team1_score < self.object.team2_score:
        self.object.result = 2
    else:
        self.object.result = 0


def from_matches_to_finished(self, group_stage):
    group_stage.matches.remove(self.object)
    group_stage.matches_finished.add(self.object)