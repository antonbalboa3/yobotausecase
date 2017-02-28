"""
Django Forms being used to handle Several actions
"""

from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    usernameInput = forms.CharField(label="Username")
    passwordInput = forms.CharField(label='Password',widget=forms.PasswordInput())
    def clean_usernameInput(self):
        usernameInput = self.cleaned_data['usernameInput']
        return usernameInput

    def clean_passwordInput(self):
        passwordInput = self.cleaned_data['passwordInput']
        return passwordInput

# Defined RegisterForm with first and last name so the provided model representation has sense
class RegisterForm(forms.Form):
    usernameInput = forms.CharField(label="Username")
    passwordInput1 = forms.CharField(label='Password',widget=forms.PasswordInput())
    passwordInput2 = forms.CharField(label='Retype Password',widget=forms.PasswordInput())
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    def clean_passwordInput2(self):
        if 'passwordInput1' in self.cleaned_data and 'passwordInput2' in self.cleaned_data :
            passwordInput1 = self.cleaned_data['passwordInput1']
            passwordInput2 = self.cleaned_data['passwordInput2']
            if passwordInput1==passwordInput2:
                return passwordInput1
        raise forms.ValidationError('Passwords are not the same')

    def clean_usernameInput(self):
        usernameInput = self.cleaned_data['usernameInput']
        if User.objects.filter(username=usernameInput).exists():
            raise forms.ValidationError('Please chose another username, username %s already exists' %  usernameInput)
        return usernameInput

# To join a game, an ID should be provided, handled here as a form
class JoinGameForm(forms.Form):
    gameId = forms.CharField(widget=forms.HiddenInput())
    def clean_gameId(self):
        gameId = self.cleaned_data['gameId']
        return gameId
