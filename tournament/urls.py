from django.urls import path
from .views import *

app_name = 'tournament'

urlpatterns = [
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/create/', TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/update', TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete', TeamDeleteView.as_view(), name='team_delete'),
]