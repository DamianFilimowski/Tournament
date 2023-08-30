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


class MatchUpdateExtraTimeForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_extra_time_score', 'team2_extra_time_score']

    def clean(self):
        cleaned_data = super().clean()
        team1_score = cleaned_data.get('team1_extra_time_score')
        team2_score = cleaned_data.get('team2_extra_time_score')

        if team1_score is None or team2_score is None:
            raise forms.ValidationError("Podaj wynik dla każdej drużyny")

        return cleaned_data


class MatchUpdatePenaltyForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_penalty_score', 'team2_penalty_score']

    def clean(self):
        cleaned_data = super().clean()
        team1_score = cleaned_data.get('team1_penalty_score')
        team2_score = cleaned_data.get('team2_penalty_score')

        if team1_score is None or team2_score is None:
            raise forms.ValidationError("Podaj wynik dla każdej drużyny")

        return cleaned_data
