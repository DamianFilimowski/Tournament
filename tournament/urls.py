from django.urls import path
from .views import *

app_name = 'tournament'

urlpatterns = [
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/create/', TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/update', TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete', TeamDeleteView.as_view(), name='team_delete'),
    path('', TournamentListView.as_view(), name='tournament_list'),
    path('create/', TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/update/', TournamentUpdateView.as_view(), name='tournament_update'),
    path('<int:pk>/delete/', TournamentDeleteView.as_view(), name='tournament_delete'),
    path('<int:pk>/start/', TournamentStart.as_view(), name='tournament_start'),
    path('<int:pk>/start/create_groups_playoff/', TournamentCreateGroupsPlayoff.as_view(),
         name='tournament_create_groups_playoff'),
    path('<int:pk>/start/create_playoff/', TournamentCreatePlayoff.as_view(),
         name='tournament_create_playoff'),
    path('match/<int:pk>/', MatchDetailView.as_view(), name='match_detail'),
    path('match/<int:pk>/update_result/', MatchUpdateResultView.as_view(), name='match_update_result'),
    path('match/<int:pk>/update_date/', MatchUpdateDateView.as_view(), name='match_update_date'),
    path('match/<int:pk>/update_scorers/', MatchUpdateScorersView.as_view(), name='match_update_scorers'),
    path('scorer_delete/<int:pk>/', MatchDeleteScorersView.as_view(), name='match_delete_scorers'),
    path('group/<int:pk>/', GroupStageDetailView.as_view(), name='groupstage_detail'),
    path('playoff/<int:pk>/', PlayoffDetailView.as_view(), name='playoff_detail')


]