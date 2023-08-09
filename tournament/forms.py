from django import forms


class SearchPersonForm(forms.Form):
    imie = forms.CharField(max_length=128, required=False)
    nazwisko = forms.CharField(max_length=128, required=False)
    nazwa_uzytkownika = forms.CharField(max_length=128, required=False)