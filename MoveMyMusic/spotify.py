from spotipy.oauth2 import SpotifyOAuth
import spotipy
import spotipy.util as util
from .config import Default
import logging

# logging.basicConfig(level=logging.DEBUG,
                    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('spotipy.client').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


class Spotify(object):
    def __init__(self, username, scope, data, source=None):
        self.export_data = data
        self.username = username
        self.source = source
        self.scope = scope


    def get_auth(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=Default.SP_CLIENT_ID, client_secret=Default.SP_CLIENT_SECRET,
                                                            redirect_uri=Default.SP_REDIRECT_URI, username=self.username, scope=self.scope,
                                                            show_dialog=True))

    def get_playlists(self):
        playlist_names_dict = {}
        playlists = self.sp.user_playlists(self.username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.username.lower():    # ONLY OWNED BY USER
                playlist_names_dict[playlist['name']] = playlist['id']
        return playlist_names_dict

    def show_tracks(self, list_type, tracks, playlist_name=None):
        for i, item in enumerate(tracks['items']):
            track = item['track']
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
            if playlist['owner']['id'] == self.username.lower():    # ONLY OWNED BY USER
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
        for title, item in self.export_data[self.source.upper()]["playlists"].items():
            track_ids = []
            new_playlist = self.sp.user_playlist_create(
                user=self.username, name=title + f'({self.source.upper()})')
            playlist_id = new_playlist['id']
            playlist_name = new_playlist['name']
            logging.debug(f"CREATED new playlist '{playlist_name}'")
            for track in item:
                results = self.sp.search(
                    q=track[0] + ' ' + track[1], type='track')
                tracks = results['tracks']
                if len(tracks['items']) != 0:
                    track_ids.append(tracks['items'][0]['id'])
                    logging.debug(
                        f"ADDED track '{tracks['items'][0]['name']}' to playlist '{playlist_name}'")
                else:
                    logging.error(
                                f"ERROR COULDNT FIND TRACK '{track[0]}-{track[1]}'")

            while len(track_ids) > 100:
                self.sp.user_playlist_add_tracks(
                    self.username, playlist_id, track_ids[:100])
                track_ids = track_ids[100:]

            self.sp.user_playlist_add_tracks(
                self.username, playlist_id, track_ids)
            logging.debug(
                f"DONE {len(track_ids)} tracks added to playlist '{playlist_name}'")

        logging.debug(f"DONE import playlists")

    def import_artists(self):
        artists = self.export_data[self.source.upper()]["artists"]
        artist_ids = []
        logging.debug(f"Total artist count: {len(artists)}")
        for artist in artists:
            logging.debug(f"START search artist '{artist}'")
            results = self.sp.search(
                q=artist + ' ', type='artist', limit=50, market='RU')
            items = results['artists']['items']
            logging.debug(
                f"TOTAL ARTIST BY NICKNAME {artist} -- {len(results['artists']['items'])}")

            # unique name or translit from russian --> No need for verification
            if len(items) != 0:
                curr_artist = items[0]
                artist_ids.append(curr_artist['id'])
                logging.debug(
                    f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                continue

            elif len(items) == 0:
                logging.debug(
                    f"EROR while search for {results}, {len(results['artists']['items'])}")
        logging.debug(f"DONE artists count: {len(artist_ids)}")
        self.sp.user_follow_artists(artist_ids)



    def import_albums(self):
        import_albums = self.export_data[self.source.upper()]["albums"]
        for item in import_albums:
            album_title = item["title"]
            artist_name = item["artist"]
            album_count = item["tracks_count"]
            try:
                results = self.sp.search(
                    q='album:' + album_title + ' ' + artist_name, type='album')
                search_artist = results['albums']['items'][0]['artists'][0]['name']
                search_title = results['albums']['items'][0]['name']
                search_uri = results['albums']['items'][0]['uri']
                search_tracks = results['albums']['items'][0]['total_tracks']
            except IndexError:
                logging.error(
                    f"COUDNT FIND ALBUM '{album_title}-{artist_name}' ON SPOTIFY")
                continue

            # Verification
            # сравниваем тайтл, имя артиста и количество песен в альбоме (source vs target)
            if search_title.casefold() == album_title.casefold() and search_artist.casefold() == artist_name.casefold() and int(album_count) == int(search_tracks):
                logging.debug(f"Album '{album_title}-{artist_name}' OK")
                # add album if not already added
                self.sp.current_user_saved_albums_add(albums=[search_uri])
                logging.debug(
                    f"DONE album '{album_title}-{artist_name}' added")



    def import_alltracks(self):
        track_ids = []
        alltracks = self.export_data[self.source.upper()]["alltracks"]
        new_playlist = self.sp.user_playlist_create(
                    user=self.username, name=f'All tracks({self.source.upper()})')
        playlist_id = new_playlist['id']
        playlist_name = new_playlist['name']
        logging.debug(f"CREATED new playlist '{playlist_name}'")
        for track in alltracks:
            results = self.sp.search(
                q=track[0] + ' ' + track[1] + ' ', type='track')
            tracks = results['tracks']
            if len(tracks['items']) != 0:
                track_ids.append(tracks['items'][0]['id'])
                logging.debug(
                    f"ADDED track '{tracks['items'][0]['name']}' to playlist '{playlist_name}'")

            elif len(tracks['items']) == 0:
                logging.error(
                    f"ERROR COULDNT FIND TRACK '{track[0]}-{track[1]}'")
        while len(track_ids) > 100:
            self.sp.user_playlist_add_tracks(
                self.username, playlist_id, track_ids[:100])
            track_ids = track_ids[100:]

        self.sp.user_playlist_add_tracks(
            self.username, playlist_id, track_ids)
        logging.debug(
            f"DONE {len(track_ids)} tracks added to playlist '{playlist_name}'")
