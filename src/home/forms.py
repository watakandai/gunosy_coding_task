from django import forms


class HomeForm(forms.Form):
    url = forms.CharField()
