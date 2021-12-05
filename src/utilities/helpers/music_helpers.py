import os
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

spotipy_id = os.getenv("SPOTIPY_ID")
spotipy_secret = os.getenv("SPOTIPY_SECRET")
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=spotipy_id, client_secret=spotipy_secret
    )
)


class Spotify:
    def getTrackID(self, track):
        track = sp.track(track)
        return track["id"]

    def getPlaylistTrackIDs(self, playlist_id):
        ids = []
        playlist = sp.playlist(playlist_id)
        for item in playlist["tracks"]["items"]:
            track = item["track"]
            ids.append(track["id"])
        return ids

    def getAlbum(self, album_id):
        album = sp.album_tracks(album_id)
        ids = []
        for item in album["items"]:
            ids.append(item["id"])
        return ids

    def getTrackFeatures(self, id):
        meta = sp.track(id)
        features = sp.audio_features(id)
        name = meta["name"]
        album = meta["album"]["name"]
        artist = meta["album"]["artists"][0]["name"]
        return f"{artist} - {name}-{album}"

    def getalbumID(self, id):
        return sp.album(id)


