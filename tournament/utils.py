import math

from django.db.models import Max

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
    group_data = sorted(group_data, key=lambda item: (-item[1]['points'],
                                                      -item[1]['goal_difference'],
                                                      -item[1]['goals_scored']))
    return group_data


def set_result(self):
    if self.object.team1_score > self.object.team2_score:
        self.object.result = 1
    elif self.object.team1_score < self.object.team2_score:
        self.object.result = 2
    else:
        self.object.result = 0
    self.object.save()


def from_matches_to_finished(self, group_stage):
    group_stage.matches.remove(self.object)
    group_stage.matches_finished.add(self.object)


def set_phase_names(playoff):
    matches = playoff.matches.all()
    max_phase = matches.aggregate(Max('phase'))['phase__max']
    for match in matches:
        if match.phase == max_phase and match.order == 2:
            match.phase_name = 'Finał'
        elif match.phase == max_phase and match.order == 1:
            match.phase_name = 'Mecz o trzecie miejsce'
        elif match.phase == max_phase - 1:
            match.phase_name = 'Półfinał'
        elif match.phase == max_phase - 2:
            match.phase_name = 'Ćwierćfinał'
        elif match.phase == max_phase - 3:
            match.phase_name = '1/8 finału'
        elif match.phase == max_phase - 4:
            match.phase_name = '1/16 finału'
        elif match.phase == max_phase - 5:
            match.phase_name = '1/32 finału'
        elif match.phase == max_phase - 6:
            match.phase_name = '1/64 finału'
        else:
            match.phase_name = '1/128 finału'
        match.save()


def set_teams_for_final_phase(self, max_phase, playoff, winner, loser):
    matches = playoff.matches.filter(phase=max_phase)
    final = matches.get(order=2)
    mini_final = matches.get(order=1)
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


def move_to_next_phase(self, playoff, winner):
    matches = playoff.matches.filter(phase=self.object.phase + 1)
    if self.object.order % 2 == 0:
        match = matches.get(order=self.object.order // 2)
        match.team2 = winner
        match.save()
    else:
        match = matches.get(order=(self.object.order + 1) // 2)
        match.team1 = winner
        match.save()


def if_player_in_tournament(tournament, team):
    tournament_players = CustomUser.objects.filter(player__tournament=tournament)
    players = team.players.all()
    for player in players:
        if player in tournament_players:
            return True
    return False
