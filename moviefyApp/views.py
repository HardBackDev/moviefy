import hashlib
import os
import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from moviefy.settings import SECRET_KEY
from moviefyApp.dtoModels import UserDto
from moviefyApp.models import Movie, CustomUser
from datetime import datetime, timedelta

import jwt

def signUp(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)        

        if form.is_valid():
            user = CustomUser()
            user.username = form.cleaned_data['username']
            user.password = form.cleaned_data['password']
            user.role = 1

            user.save()

            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'user': None})

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = CustomUser.objects.get(username=username)
                hash_object = hashlib.new('sha256')
                hash_object.update(password.encode('utf-8'))
                hashed_password = hash_object.hexdigest()

                if not user.password == hashed_password:
                    form.add_error('password', "Invalid password.")
                    return render(request, 'login.html', {'form': form, 'user': None})

                dt = datetime.now() + timedelta(days=1)

                token = jwt.encode({
                    'role': user.role,
                    'username': user.username,
                    'exp': int(dt.timestamp())
                }, settings.SECRET_KEY, algorithm='HS256')
                response = redirect('home')
                response.set_cookie('jwt_token', token, httponly=False)
                return response

            except CustomUser.DoesNotExist:
                form.add_error('username', 'Invalid username.')
                return render(request, 'login.html', {'form': form, 'user': None})
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form, 'user': None})

def topTenMovies(request):
    title = request.GET.get('title')
    movies = Movie.objects.order_by('-rating')[:10]
    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm(), 'user': user})

    if title:
        movies = movies.filter(title__icontains=title)
    
    return render(request, 'movies.html', {'movies': movies, 'user': user})

def home(request):
    user = authorize(request)
    if(not user):
        return render(request, 'welcome.html', {'user': user})

    return movies(request)

def likeMovie(request, id):
    movieModel = Movie.objects.get(pk=id)
    movieModel.rating = movieModel.rating + 1
    movieModel.save()
    return movie(request, id)

def movies(request):
    title = request.GET.get('title')
    genres = request.GET.get('genres')
    movies = Movie.objects.all()

    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm()})
    
    if genres:
        genres_list = [genre.strip() for genre in genres.split(',')]
        
        for genre in genres_list:
            movies = movies.filter(genres__icontains=genre)

    if title:
        movies = Movie.objects.filter(title__icontains=title)

    return render(request, 'movies.html', {'movies': movies, 'user': user})

def movie(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm()})

    return render(request, 'movie_details.html', {'movie': movie, 'user': user})

from .forms import MovieCreateForm, MovieUpdateForm, UserLoginForm, UserRegisterForm

def create_movie(request):
    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm()})
    if user.role != 2:
        return render(request, 'login.html', {'form': UserLoginForm()})

    if request.method == 'POST':
        form = MovieCreateForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MovieCreateForm()
    
    return render(request, 'create_movie.html', {'form': form})

def delete_movie(request, movie_id):
    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm()})
    if user.role != 2:
        return render(request, 'login.html', {'form': UserLoginForm()})
    
    movie = Movie.objects.get(pk=movie_id)
    movie.delete()
    return redirect('home')

def update_movie(request, id):
    user = authorize(request)
    if(not user):
        return render(request, 'login.html', {'form': UserLoginForm()})
    if user.role != 2:
        return render(request, 'login.html', {'form': UserLoginForm()})
    
    movie = Movie.objects.get(pk=id)
    if request.method == 'POST':
        form = MovieUpdateForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            
            return redirect('home')
    else:
        form = MovieUpdateForm(instance=movie)
    
    return render(request, 'update_movie.html', {'form': form})

def stream_video(request, video_path):
    full_path = os.path.join(os.getcwd(), 'moviefyApp/static/videos', video_path)

    if not os.path.exists(full_path):
        return HttpResponseNotFound("File not found")

    response = HttpResponse(content_type='video/mp4')
    video_size = os.path.getsize(full_path)

    if 'HTTP_RANGE' in request.META:
        range_header = request.META['HTTP_RANGE']
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        start_byte = int(range_match.group(1))
        end_byte = min(int(range_match.group(2)) if range_match.group(2) else video_size - 1, video_size - 1)

        response.status_code = 206
        response['Content-Range'] = f'bytes {start_byte}-{end_byte}/{video_size}'
        response['Content-Length'] = end_byte - start_byte + 1

        with open(full_path, 'rb') as video_stream:
            video_stream.seek(start_byte)
            response.content = video_stream.read(end_byte - start_byte + 1)
    else:
        with open(full_path, 'rb') as video_file:
            response.content = video_file.read()

    return response

def authorize(request) -> UserDto:
    jwt_token = request.COOKIES.get('jwt_token')
    if not jwt_token:
        return
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
    except:
        return
    
    return UserDto(payload['username'], payload['role'])


class PartialFileResponse(FileResponse):
    def __init__(self, file, *args, **kwargs):
        super().__init__(file, *args, **kwargs)

    def __iter__(self):
        self.filelike.seek(self.start_byte)
        if self.end_byte is None:
            yield from super().__iter__()
        else:
            remaining_bytes = self.end_byte - self.start_byte + 1
            while remaining_bytes > 0:
                chunk = self.filelike.read(min(remaining_bytes, 8192))
                if not chunk:
                    break
                remaining_bytes -= len(chunk)
                yield chunk


