"""Offers pause and unpause functions for my spotify account"""
import spotipy
import config as c
from spotipy.oauth2 import SpotifyOAuth

auth_manager = SpotifyOAuth(client_id=c.CLIENT_ID, client_secret=c.CLIENT_SECRET, redirect_uri=c.REDIRECT_URI, scope=c.SCOPEs)
sp = spotipy.Spotify(auth_manager=auth_manager)

def spotify_pause():
    """Pauses my spotify account"""
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            sp.pause_playback(device['id'])

def spotify_play():
    """Unpauses my spotify account"""
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            sp.start_playback(device['id'])

def start_stop_song():
    """Unpauses if paused and vice versa"""
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            isPlaying = sp.current_user_playing_track()
            if isPlaying['is_playing']:
                sp.pause_playback(device['id'])
            else:
                sp.start_playback(device['id'])

def skip_song():
    devices = sp.devices()
    for device in devices['devices']:
        sp.next_track(device['id'])

if __name__ == '__main__':
    start_stop_song()