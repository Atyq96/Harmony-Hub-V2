from django.contrib import admin
from django.urls import path,include

from .views import spotify_login,callback,top_tracks

urlpatterns = [
    path('login/', spotify_login,name = 'login'),
    path('callback/', callback,name = 'callback'),
    path('top_tracks/', top_tracks,name = 'top_tracks'),
  
]