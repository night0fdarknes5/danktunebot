import os
from sql_handler import *
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

bangers_and_gash = spotify.user_playlist(user = '1274812788', playlist_id = 'https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k')

print(bangers_and_gash)

