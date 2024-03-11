from django.db import models
import jwt

from datetime import datetime, timedelta

from django.conf import settings 

from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    genres = models.CharField(max_length=1000)
    poster_url = models.CharField(max_length=25500)
    video_path = models.CharField(max_length=2550)
    release_date = models.DateField()
    rating = models.IntegerField(default=0)

class CustomUser(models.Model):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    password = models.CharField(max_length=1000)
    role = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

