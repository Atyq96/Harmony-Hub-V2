import requests
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
REDIRECT_URI = "http://127.0.0.1:8000/callback/"

CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

def spotify_login(request):
    scope = "user-top-read user-read-recently-played user-read-private user-read-email user-library-read"
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

def callback(request):
    code = request.GET.get('code')
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=data)
    response_data = response.json()
    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')
    # Save tokens to user session or database
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    return redirect(reverse('top_tracks'))

def top_tracks(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'Access token not found'}, status=401)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(f"{SPOTIFY_API_URL}/me/top/tracks?limit=5", headers=headers)
    top_tracks_data = response.json().get('items', [])

    return JsonResponse({'top_tracks': top_tracks_data})

def recommended_tracks(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('spotify-login')
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(f"{SPOTIFY_API_URL}/me/top/tracks?limit=5", headers=headers)
    top_tracks_data = response.json()
    track_ids = [track['id'] for track in top_tracks_data['items']]
    response = requests.get(f"{SPOTIFY_API_URL}/recommendations?seed_tracks={','.join(track_ids)}&limit=5", headers=headers)
    recommended_tracks_data = response.json()
    return render(request, 'recommended_tracks.html', {'recommended_tracks': recommended_tracks_data['tracks']})

