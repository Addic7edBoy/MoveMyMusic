import sys
import spotipy
import spotipy.util as util
from config import Default
import logging
import collections
import json
import pprint
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('spotipy.client').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


class Spotify(object):
    def __init__(self, username, scope, data, source=None):
        self.export_data = data
        self.username = Default.SP_USERNAME
        self.source = source
        self.scope = 'user-library-modify user-library-read user-follow-read user-follow-modify playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative'
        token = util.prompt_for_user_token(
            self.username,
            self.scope,
            client_id=Default.SP_CLIENT_ID,
            client_secret=Default.SP_CLIENT_SECRET,
            redirect_uri='http://example.com')
        if token:
            logging.debug(f'token OK: (token)')
            self.sp = spotipy.Spotify(auth=token)
        else:
            logging.error(f"Can't get token for {self.username}")

    def show_tracks(self, list_type, tracks, playlist_name=None):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("   %d %32.32s %s" %
                  (i, track['artists'][0]['name'], track['name']))
            if playlist_name:
                self.export_data["SP"][list_type][playlist_name].append(
                    [track['name'], track['artists'][0]['name']])
            else:
                self.export_data["SP"][list_type].append(
                    [track['name'], track['artists'][0]['name']])

    def export_playlists(self):
        playlists = self.sp.user_playlists(self.username)
        logging.debug(f"START export onwned playlists")
        for playlist in playlists['items']:
            print(playlist['name'])
            if playlist['owner']['id'] == self.username.lower():    # ONLY OWNED BY USE
                logging.debug(f"START export playlists '{playlist['name']}'")
                self.export_data["SP"]["playlists"][playlist['name']] = []
                results = self.sp.playlist(
                    playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                logging.debug('showing tracks')
                self.show_tracks('playlists', tracks, playlist['name'])
                while tracks['next']:
                    tracks = self.sp.next(tracks)
                    self.show_tracks('playlists', tracks, playlist['name'])
                logging.debug(
                    f"DONE export playlist '{playlist['name']}'; {playlist['tracks']['total']}:{len(self.export_data['SP']['playlists'][playlist['name']])}")

    def export_alltracks(self):
        self.export_data["SP"]["alltracks"] = []
        tracks = self.sp.current_user_saved_tracks(limit=50)
        logging.debug(f"START export playlists 'My favorites'")
        self.show_tracks('alltracks', tracks)
        while tracks['next']:
            tracks = self.sp.next(tracks)
            self.show_tracks('alltracks', tracks)
        logging.debug(
            f"DONE export playlist 'My favorites', Total: {len(self.export_data['SP']['alltracks'])}")

    def export_artists(self):
        self.export_data["SP"]["artists"] = []
        results = self.sp.current_user_followed_artists()
        artists = results['artists']
        for item in artists['items']:
            print(item['name'])
            self.export_data["SP"]["artists"].append(item['name'])
        while artists['next']:
            logging.debug('Exporting next page of artists...')
            artists = self.sp.next(artists)['artists']
            for item in artists['items']:
                print(item['name'])
                self.export_data["SP"]["artists"].append(item['name'])
        logging.debug(
            f"DONE export artists, Total: {len(self.export_data['SP']['artists'])}")

    def export_albums(self):
        albums = self.sp.current_user_saved_albums()
        for item in albums['items']:
            album_title = item['album']['name']
            artist_name = item['album']['artists'][0]['name']
            tracks = item['album']['tracks']['items']
            self.export_data["SP"]["albums"].append({
                                                    "title": album_title,
                                                    "artist": artist_name,
                                                    "tracks_count": len(tracks)
                                                    })
            # self.export_data["SP"]["albums"][album_title + ' - ' + artist_name] = [track['name'] for track in tracks]
        while albums['next']:
            logging.debug('Exporting next page of albums...')
            albums = self.sp.next(albums)
            for item in albums['items']:
                album_title = item['album']['name']
                artist_name = item['album']['artists'][0]['name']
                tracks = item['album']['tracks']['items']
                self.export_data["SP"]["albums"].append({
                    "title": album_title,
                    "artist": artist_name,
                    "tracks_count": len(tracks)
                })
                # self.export_data["SP"]["albums"][album_title + ' - ' + artist_name] = [track['name'] for track in tracks]
        logging.debug(
            f"DONE export albums, Total: {len(self.export_data['SP']['albums'])}")

    def unfollow_all(self):
        results = self.sp.current_user_followed_artists()
        artist_tuple = [(item['id'], item['name'])
                        for item in results['artists']['items']]
        artist_ids = [item['id'] for item in results['artists']['items']]
        print(artist_tuple)
        print(artist_ids)
        self.sp.user_unfollow_artists(artist_ids)

    def import_playlists(self):
        for item in ['VK', 'YM']:
            for title, tracks in self.export_data[item]["playlists"]:
                track_ids = []
                for playlist in playlists:
                    track_ids = []
                    new_playlist = self.sp.user_playlist_create(
                        user=self.username, name=playlist + '(Y.music)')
                    playlist_id = new_playlist['id']
                    playlist_name = new_playlist['name']
                    logging.debug(f"CREATED new playlist '{playlist_name}'")

                    for track in playlists[playlist]:
                        results = self.sp.search(
                            q='artist:' + track[0] + ' ' + 'track:' + track[1] + ' ' + 'album:' + track[2], type='track')
                        tracks = results['tracks']
                        if len(tracks['items']) == 1:
                            track_ids.append(tracks['items'][0]['id'])
                            logging.debug(
                                f"ADDED track '{tracks['items'][0]['name']}' to playlist '{playlist_name}'")
                        elif len(tracks['items']) > 1:
                            artist_name = tracks['items'][0]['artists'][0]['name']
                            track_title = tracks['items'][0]['name']
                            album_title = tracks['items'][0]['album']['name']
                            if artist_name.casefold() == track[0] and track_title.casefold() == track[1].casefold() and album_title.casefold() == track[2].casefold():
                                track_ids.append(tracks['items'][0]['id'])
                                logging.debug(
                                    f"ADDED track '{track_title}' to playlist '{playlist_name}'")
                            else:
                                logging.warning(
                                    f"Track '{artist_name}-{track_title}' not in best match; verification needed")
                        elif len(tracks['items']) == 0:
                            logging.error(
                                f"ERROR COULDNT FIND TRACK '{track[0]}-{track[1]}'")
                    self.sp.user_playlist_add_tracks(
                        self.username, playlist_id, track_ids)
                    logging.debug(
                        f"DONE {len(track_ids)} tracks added to playlist '{playlist_name}'")
                logging.debug(f"DONE import playlists")

    def import_artist(self, dt):
        artists = dt['artists']
        artist_ids = []
        logging.debug(f"Total artist count: {len(artists)}")
        for artist in artists:
            logging.debug(f"START search artist '{artist}'")
            results = self.sp.search(
                q=artist, type='artist', market='US', limit=50)
            items = results['artists']['items']
            logging.debug(
                f"TOTAL ARTIST BY NICKNAME {artist} -- {len(results['artists']['items'])}")

            # unique name or translit from russian --> No need for verification
            if len(items) == 1:
                curr_artist = items[0]
                artist_ids.append(curr_artist['id'])
                logging.debug(
                    f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                continue

            # Many artists with same name/pattern in name --> Needs verifivcation
            elif len(items) > 1:
                if items[0]['name'] == artist or items[0]['name'].casefold() == artist.casefold():
                    logging.debug(f"{items[0]['name']} <--> {artist} OK")
                    curr_artist = items[0]
                    artist_ids.append(curr_artist['id'])
                    logging.debug(
                        f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                    continue
                else:
                    logging.debug(f"{items[0]['name']} != {artist} NOT OK")
                    for item in items:
                        if item['name'] == artist or item['name'].casefold() == artist.casefold():
                            curr_artist = item
                            artist_ids.append(curr_artist['id'])
                            logging.debug(f"{item['name']} <--> {artist} OK")
                            logging.debug(
                                f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                            break
                        else:
                            logging.debug(f"{item['name']} != {artist} NOT OK")
                            continue
            # Ooops!
            elif len(items) == 0:
                logging.debug(
                    f"EROR while search for {results}, {len(results['artists']['items'])}")
        logging.debug(f"DONE artists count: {len(artist_ids)}")
        self.sp.user_follow_artists(artist_ids)

    def import_albums(self, dt):
        import_albums = dt['albums']
        for k, v in import_albums.items():
            title, artist = re.split(' - ', k)
            try:
                results = self.sp.search(
                    q='album:' + title + ' ' + 'artist:' + artist, type='album')
                artist_name = results['albums']['items'][0]['artists'][0]['name']
                # artist_uri = results['albums']['items'][0]['artists'][0]['uri']
                album_title = results['albums']['items'][0]['name']
                album_uri = results['albums']['items'][0]['uri']
                total_tracks = results['albums']['items'][0]['total_tracks']
            except IndexError:
                logging.error(
                    f"COUDNT FIND ALBUM '{title}-{artist}' ON SPOTIFY")
                continue

            #   Verification
            if title.casefold() == album_title.casefold() and artist.casefold() == artist_name.casefold() and int(len(v)) == int(total_tracks):
                logging.debug(f"Album '{title}-{artist}' OK")
                # add album if not already added
                self.sp.current_user_saved_albums_add(albums=[album_uri])
                logging.debug(
                    f"DONE album '{album_title}-{artist_name}' added")
