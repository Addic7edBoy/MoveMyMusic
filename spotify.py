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
    def __init__(self):
        self.export_SP = collections.defaultdict(dict)
        self.username = Default.SP_USERNAME
        self.scope = 'user-library-modify user-library-read user-follow-read user-follow-modify playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative'
        self.token = util.prompt_for_user_token(
                                    self.username,
                                    self.scope,
                                    client_id=Default.SP_CLIENT_ID,
                                    client_secret=Default.SP_CLIENT_SECRET,
                                    redirect_uri='http://example.com')
        if self.token:
            logging.debug(f'token OK: ({self.token})')
            self.sp = spotipy.Spotify(auth=self.token)
        else:
            logging.error(f"Can't get token for {self.username}")

    def show_tracks(self, tracks, playlist_name):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))
            self.export_SP['playlist'][playlist_name].append([track['name'], track['artists'][0]['name']])

    def export_playlists(self):
        playlists = self.sp.user_playlists(self.username)
        logging.debug(f"START export onwned playlists")
        for playlist in playlists['items']:
            print(playlist['name'])
            if playlist['owner']['id'] == self.username.lower():    # ONLY OWNED BY USE
                logging.debug(f"START export playlists '{playlist['name']}'")
                self.export_SP['playlist'][playlist['name']] = []
                results = self.sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                logging.debug('showing tracks')
                self.show_tracks(tracks, playlist['name'])
                while tracks['next']:
                    tracks = self.sp.next(tracks)
                    self.show_tracks(tracks, playlist['name'])
                logging.debug(F"DONE export playlist '{playlist['name']}'; {playlist['tracks']['total']}:{len(self.export_SP['playlist'][playlist['name']])}")

    def export_tracks(self):
        self.export_SP['playlist']['My favorites'] = []
        results = self.sp.current_user_saved_tracks(limit=50)
        logging.debug(f"START export playlists 'My favorites'")
        for item in results['items']:
            track = item['track']
            self.export_SP['playlist']['My favorites'].append([track['name'], track['artists'][0]['name']])
            print(track['name'] + ' - ' + track['artists'][0]['name'])
        logging.debug(f"DONE export playlists 'My favorites'")

    def export_artist(self):
        self.export_SP['artists'] = []
        results = self.sp.current_user_followed_artists()
        for item in results['artists']['items']:
            print(item['name'])
            self.export_SP['artists'].append(item['name'])
        logging.debug(f"Total artist count: {len(self.export_SP['artists'])}")

    def export_albums(self):
        results = self.sp.current_user_saved_albums()
        items = results['items']
        for item in items:
            album_title = item['album']['name']
            artist_name = item['album']['artists'][0]['name']
            tracks = item['album']['tracks']['items']
            self.export_SP['albums'][album_title + ' - ' + artist_name] = [track['name'] for track in tracks]

    def artist_test(self):
        pp = pprint.PrettyPrinter(indent=4)
        statement = 'RAM'
        results = self.sp.search(q=statement, type='artist', limit=50)
        pp.pprint(results)
        print(len(results['artists']['items']))
        test1 = []
        with open('test.txt', 'a+') as f:
            for item in results['artists']['items']:
                test1.append(item['name'])
            f.write('\n')
            f.write(' '.join(test1))
            f.write('\n')

    def unfollow_all(self):
        results = self.sp.current_user_followed_artists()
        artist_tuple = [(item['id'], item['name']) for item in results['artists']['items']]
        artist_ids = [item['id'] for item in results['artists']['items']]
        print(artist_tuple)
        print(artist_ids)
        self.sp.user_unfollow_artists(artist_ids)

    def import_playlists(self, dt):
        playlists = dt['playlists']

    def import_artist(self, dt):
        artists = dt['artists']
        artist_ids = []
        logging.debug(f"Total artist count: {len(artists)}")
        for artist in artists:
            logging.debug(f"START search artist '{artist}'")
            results = self.sp.search(q=artist, type='artist', market='US', limit=50)
            items = results['artists']['items']
            logging.debug(f"TOTAL ARTIST BY NICKNAME {artist} -- {len(results['artists']['items'])}")

            # unique name or translit from russian --> No need for verification
            if len(items) == 1:
                curr_artist = items[0]
                artist_ids.append(curr_artist['id'])
                logging.debug(f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                continue

            # Many artists with same name/pattern in name --> Needs verifivcation
            elif len(items) > 1:
                if items[0]['name'] == artist or items[0]['name'].casefold() == artist.casefold():
                    logging.debug(f"{items[0]['name']} <--> {artist} OK")
                    curr_artist = items[0]
                    artist_ids.append(curr_artist['id'])
                    logging.debug(f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                    continue
                else:
                    logging.debug(f"{items[0]['name']} != {artist} NOT OK")
                    for item in items:
                        if item['name'] == artist or item['name'].casefold() == artist.casefold():
                            curr_artist = item
                            artist_ids.append(curr_artist['id'])
                            logging.debug(f"{item['name']} <--> {artist} OK")
                            logging.debug(f"DONE search artist '({curr_artist['name']}-{artist}):{curr_artist['id']}'")
                            break
                        else:
                            logging.debug(f"{item['name']} != {artist} NOT OK")
                            continue
            # Ooops!
            elif len(items) == 0:
                logging.debug(f"EROR while search for {results}, {len(results['artists']['items'])}")
        logging.debug(f"DONE artists count: {len(artist_ids)}")
        self.sp.user_follow_artists(artist_ids)

    def import_albums(self, dt):
        import_albums = dt['albums']
        for k, v in import_albums.items():
            title, artist = re.split(' - ', k)
            try:
                results = self.sp.search(q='album:' + title + ' ' + 'artist:' + artist, type='album')
                artist_name = results['albums']['items'][0]['artists'][0]['name']
                artist_uri = results['albums']['items'][0]['artists'][0]['uri']
                album_title = results['albums']['items'][0]['name']
                album_uri = results['albums']['items'][0]['uri']
                total_tracks = results['albums']['items'][0]['total_tracks']
            except IndexError:
                logging.error(f"COUDNT FIND ALBUM '{title}-{artist}' ON SPOTIFY")
                continue

            #   Verification
            if title.casefold() == album_title.casefold() and artist.casefold() == artist_name.casefold() and int(len(v)) == int(total_tracks):
                logging.debug(f"Album '{title}-{artist}' OK")
                # add album if not already added
                self.sp.current_user_saved_albums_add(albums=[album_uri])
                logging.debug(f"DONE album '{album_title}-{artist_name}' added")


if __name__ == '__main__':
    SP = Spotify()
    SP.export_artist()
    SP.export_albums()
    SP.export_tracks()
    SP.export_playlists()
    with open('export_SP.json', 'w', encoding='utf-8') as f:
        json.dump(SP.export_SP, f, indent=4, ensure_ascii=False)
    # SP.export_albums()
    # if Default.START == 'YM':
    #     with open('export_YM.json') as f:
    #         dt = json.load(f)
    # # SP.import_artist(dt)
    # SP.import_albums(dt)
