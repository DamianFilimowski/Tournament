from django import forms

from tournament.models import Match


class SearchPersonForm(forms.Form):
    imie = forms.CharField(max_length=128, required=False)
    nazwisko = forms.CharField(max_length=128, required=False)
    nazwa_uzytkownika = forms.CharField(max_length=128, required=False)


class SearchTeamForm(forms.Form):
    nazwa = forms.CharField(max_length=128, required=False)
    krotka_nazwa = forms.CharField(max_length=128, required=False)


class MatchUpdateResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score']

    def clean(self):
        cleaned_data = super().clean()
        team1_score = cleaned_data.get('team1_score')
        team2_score = cleaned_data.get('team2_score')

        if team1_score is None or team2_score is None:
            raise forms.ValidationError("Podaj wynik dla każdej drużyny")

        return cleaned_data

