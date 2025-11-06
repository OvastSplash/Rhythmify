from django import forms
from SpotifyController.services import SpotifyService
from .models import CustomUser
from .services import UserService
from django.contrib.auth import authenticate
import secrets
import string

class LoginForm(forms.ModelForm):
    user_login = forms.CharField(
        label='Login',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'off',
        })
    )
    password = forms.CharField(
        label="Password",
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('user_login', 'password')

    def clean(self):
        user_login = self.cleaned_data.get('user_login')
        password = self.cleaned_data.get('password')

        if not password:
            raise forms.ValidationError("Password cannot be empty")

        if user_login:
            user = authenticate(user_login=user_login, password=password)

            if user is None:
                raise forms.ValidationError("login or password is invalid")

            if not user.is_active:
                raise forms.ValidationError("User is not active")

            return self.cleaned_data

        else:
            raise forms.ValidationError("login cannot be empty")

class RegisterForm(forms.ModelForm):
    user_login = forms.CharField(
        label='Login',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'login',
        })
    )

    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        })
    )

    password = forms.CharField(
        label='Password',
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )

    check_password = forms.CharField(
        label="Check password",
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Check password',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('user_login', 'username', 'password')

    def clean_login(self):
        user_login = self.cleaned_data.get('user_login')

        if CustomUser.objects.filter(user_login=user_login).exists():
            raise forms.ValidationError("login already exists")

        if not user_login:
            raise forms.ValidationError("login cannot be empty")

        return user_login

    def clean(self):
        password = self.cleaned_data.get('password')
        check_password = self.cleaned_data.get('check_password')

        if not password or not check_password:
            raise forms.ValidationError("Password cannot be empty")

        if password != check_password:
            raise forms.ValidationError("Password does not match")

        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password'))

        if commit:
            user.save()
        return user

class ConfirmRegisterForm(forms.ModelForm):
    user_login = forms.CharField(
        label='Login',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your login',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('user_login', )

    def clean(self):
        cleaned_data = super().clean()
        user_login = cleaned_data.get('user_login')

        if user_login:
            if CustomUser.objects.filter(user_login=user_login).exists():
                raise forms.ValidationError("login already exists")

            return cleaned_data

        raise forms.ValidationError("login cannot be empty")

    def save_with_spotify_data(self, data, commit=True):
        user: CustomUser = super().save(commit=False)

        user.access_token, user.refresh_token, user.token_expires_at = (
            SpotifyService.get_tokens(data))

        user.token_expires_at = SpotifyService.convert_expires_at(user.token_expires_at)

        user.username, user.spotify_id, user.spotify_url, user.followers, image_url = (
            SpotifyService.get_user_info(data))

        user.user_image = UserService.update_user_image(user, image_url, save=False)

        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(21))
        user.set_password(password)

        if commit:
            user.save()
            authenticate(username=user.username, password=password)

        return user