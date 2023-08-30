from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import CustomUser
from .serializers import UserSerializer

class UserListAPIView(APIView):
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
