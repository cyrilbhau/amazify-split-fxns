import logging
import requests
import spotipy
import urllib.parse
import Flask
import webbrowser

from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect

app = Flask(__name__)
app.secret_key = "fakekey"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify Constants
# Removed actual keys to allow pushing to Github
SPOTIFY_PLAYLIST_ID = ""
SPOTIFY_CLIENT_ID = ""
SPOTIFY_SECRET = ""
SPOTIFY_AUTH_TOKEN = ""
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_BASE_ENDPOINT = 'https://api.spotify.com/v1'
SPOTIFY_SEARCH_ENDPOINT = f'{SPOTIFY_BASE_ENDPOINT}/search'
SPOTIFY_ME_ENDPOINT = f'{SPOTIFY_BASE_ENDPOINT}/me'
SPOTIFY_REDIRECT_URL = 'http://127.0.0.1:5000/callback'
SPOTIFY_STATE_KEY = 'spotify_auth_state'
SPOTIFY_API_SCOPES = [
    'user-read-private',
    'user-read-email',
    'playlist-modify-private',
    'playlist-modify-public',
]

@app.route('/callback')
def authenticate_spotify ():
    auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                              client_secret=SPOTIFY_SECRET,
                              redirect_uri=SPOTIFY_REDIRECT_URL,
                              scope=SPOTIFY_API_SCOPES,
                              show_dialog=True)
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    if request.args.get("code"):
        # Assuming the user authorized the app, Spotipy handles the exchange
        auth_manager.get_access_token(request.args["code"])
        return "Spotify authentication successful."
    else:
        return "Spotify authentication failed."

def read_songs():
    names = []
    with open("testfile.txt") as f:
        for name in f.read().split("\n"):
            name = name[2:]
            names.append(name)
    return names

def search_song(song_name):
    uri_encoded_name = urllib.parse.quote(song_name)
    endpoint = "{}?q={}&type=track&market=IN&limit=1".format(SPOTIFY_SEARCH_ENDPOINT, uri_encoded_name)
    api_response = requests.get(url=endpoint, headers={
        "Authorization": "Bearer {}".format(SPOTIFY_AUTH_TOKEN)
    })
    response_json = api_response.json()
    track_uri = response_json['tracks']['items'][0]['uri']
    print("Extracted Track URI:", track_uri)
    return track_uri

def add_song_to_playlist(track_uri, sp):
    print(f"Adding {track_uri} to playlist...")
    try:
        sp.playlist_add_items(playlist_id=SPOTIFY_PLAYLIST_ID, items=[track_uri])
        print(f"Successfully added {track_uri} to playlist.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Failed to add {track_uri} to playlist: {e}")

def main():
    app.run(debug=True, port=5000)
    sp = authenticate_spotify()
    song_names = read_songs()
    for song_name in song_names:
        track_uri = search_song(song_name)
        add_song_to_playlist(sp, track_uri)
        
if __name__ == "__main__":
    main()
