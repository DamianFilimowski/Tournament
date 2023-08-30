from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='user-list-api'),

]