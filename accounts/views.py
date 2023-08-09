from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from accounts.forms import AddUserModelForm
from accounts.models import CustomUser
from tournament.forms import SearchPersonForm


# Create your views here.


class ProfileView(LoginRequiredMixin, View):
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


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'accounts:profile')
            return redirect(redirect_url)
        return render(request, 'accounts/login.html')


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class UserListView(ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        first_name = self.request.GET.get('imie', '')
        last_name = self.request.GET.get('nazwisko', '')
        username = self.request.GET.get('nazwa_uzytkownika', '')
        queryset = queryset.filter(first_name__icontains=first_name, last_name__icontains=last_name,
                                   username__icontains=username)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchPersonForm(self.request.GET)
        return context


class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'accounts/user_detail.html'
