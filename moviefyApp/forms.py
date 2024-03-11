from datetime import datetime, timedelta
import hashlib
from django import forms
from .models import Movie, CustomUser

class MovieUpdateForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'genres', 'poster_url', 'video_path', 'release_date']

class MovieCreateForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = Movie
        fields = ['title', 'description', 'genres', 'poster_url', 'video_path', 'release_date']

class UserRegisterForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        print('starting hashing passsword: ' + password)
        hash_object = hashlib.new('sha256')
        hash_object.update(password.encode('utf-8'))
        hashed_password = hash_object.hexdigest()

        return hashed_password

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class UserLoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']

        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        return password
