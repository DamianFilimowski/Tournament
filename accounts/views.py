from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View

from accounts.forms import AddUserModelForm


# Create your views here.


class ProfileView(View):
    def get(self, request):
        return render(request, 'accounts/profile.html')


class RegisterView(View):
    def get(self, request):
        form = AddUserModelForm()
        return render(request, 'accounts/register.html', {'form':form})

    def post(self, request):
        form = AddUserModelForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('accounts:profile')
        return render(request, 'accounts/register.html', {'form':form})