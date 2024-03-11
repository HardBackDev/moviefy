from django.contrib import admin
from moviefyApp.models import CustomUser, Movie

admin.site.register(Movie)
admin.site.register(CustomUser)