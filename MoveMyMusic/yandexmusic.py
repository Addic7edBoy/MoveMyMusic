# -*- coding: utf-8 -*-
import collections
from yandex_music.client import Client
from .config import Default
import json
import logging
import requests
import time


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('yandex_music').setLevel(logging.ERROR)


class YandexMusic(object):
    def __init__(self, login, password, export_data, playlists_l, source=None):
        self.failed = []
        self.my_id = None
        self.client = Client.from_credentials(login, password)
        self.export_data = export_data
        self.playlists_l = playlists_l
        self.source = source


    # Проверяем существует ли нужный плейлист. Нет - создаем с нужным тайтлом и возвращаем ID, Да - просто возвращаем ID
    def check_playlist(self, playlist_title):
        logging.debug(f"Checking if playlist '{playlist_title}' exists")
        my_playlists = self.client.users_playlists_list()
        for playlist in my_playlists:
            if playlist['title'] == playlist_title:
                logging.debug(f'playlist "{playlist_title}" exists; its id: "{playlist["kind"]}"')
                return (playlist['kind'], playlist['revision'])

        playlist_new = self.client.users_playlists_create(title=playlist_title)
        logging.debug(f"playlist '{playlist_title}' not found; created with id: '{playlist_new['kind']}'")
        return (playlist_new['kind'], playlist_new['revision'])



    # Поиск информации об исполнителе. Возвращает json файл: имя, ID, все альбомы, все треки
    def find_artist(self, artist):
        info_dict = collections.defaultdict(dict)
        artist_info = self.client.search(text=artist, nocorrect=True, type_='artist')['artists']['results'][0]
        artist_id = artist_info['id']
        artist_albums = self.client.artists_direct_albums(artist_id=artist_id)['albums']
        artist_tracks = self.client.artists_tracks(artist_id=artist_id, page_size=100)['tracks']
        info_dict['artist_name'] = artist.lower()
        info_dict['artist_id'] = artist_id
        for album in artist_albums:
            info_dict['artist_albums'][album['title'].lower()] = {
                                                        'album_id': album['id'],
                                                        'track_count': album['track_count']}
        for track in artist_tracks:
            info_dict['artist_tracks'][track['title'].lower()] = [track['id'], track['albums'][0]['title'].lower(), track['albums'][0]['id']]

        with open('moo.json', 'w', encoding='utf-8') as f:
            json.dump(info_dict, f, indent=4, ensure_ascii=False)
        return info_dict

    def import_albums(self):
        import_albums = self.export_data[self.source.upper()]["albums"]
        for item in import_albums:
            album_title = item["title"]
            artist_name = item["artist"]
            album_count = item["tracks_count"]
            try:
                search_text = album_title + ' ' + artist_name
                results = self.client.search(text=search_text, nocorrect=True, type_="album")['albums']['results'][0]
                search_title = results.title
                search_artist = results.artists[0].name
                search_count = results.track_count
            except IndexError:
                logging.error(
                    f"COUDNT FIND ALBUM '{album_title}-{artist_name}' ON YANDEX MUSIC")
                continue
            if search_title.casefold() == album_title.casefold() and search_artist.casefold() == artist_name.casefold() and int(album_count) == int(search_count):
                logging.debug(f"Album '{album_title}-{artist_name}' OK")
                album_id = results.id
                # add album if not already added
                self.client.users_likes_albums_add(album_ids=album_id)
                logging.debug(
                    f"DONE album '{album_title}-{artist_name}' added")

    def import_artists(self):
        artists = self.export_data[self.source.upper()]["artists"]
        for artist in artists:
            logging.debug(f"START search artist '{artist}'")
            try:
                results = self.client.search(text=artist, type_='artist', nocorrect=False)['artists']['results'][0]
                search_artist = results.name # for verification in future
                logging.debug(f"found search_artist {search_artist}")
                artist_id = results.id
                self.client.users_likes_artists_add(artist_ids=artist_id)
                logging.debug(f"{search_artist} ADDED OK")
            except (IndexError, TypeError) as e:
                logging.error(
                    f"COUDNT FIND ARTIST '{artist}' ON YANDEX MUSIC")
                logging.error(e)
                continue

    def import_playlists(self):
        import_tracks = ''
        url='https://music.yandex.ru/handlers/import.jsx'
        playlists = self.export_data[self.source.upper()]["playlists"]
        for title, tracks in playlists.items():
            playlist_id, playlist_rev = self.check_playlist(title)
            for item in tracks:
                import_tracks += ' '.join(item) + '\n'
            string_of_songs=import_tracks.replace(' ','+')
            json_values={
                'content':string_of_songs
            }
            r1_import=requests.post(url,json=json_values)

            # GET
            id_import=json.loads(r1_import.text)['importCode']
            params={
                'code':id_import
            }
            resp=requests.get(url=url, params=params)
            resp = json.loads(resp.text)
            logging.debug(f"{resp['status']}")

            while True:
                if resp['status'] == 'in-progress':
                    logging.debug(f"{resp['status']}")
                    time.sleep(2)
                    r2_import=requests.get(url=url, params=params)
                    resp = json.loads(r2_import.text)
                elif resp['status'] == 'done':
                    logging.debug(f"{resp['status']}")
                    trackIds = resp['trackIds']
                    print(trackIds)
                    break

            for trackId in trackIds:
                self.client.users_playlists_insert_track(playlist_id, trackId.split(':')[0], trackId.split(':')[1], revision=playlist_rev)
                playlist_rev += 1


    def import_alltracks(self):
        alltracks = self.export_data[self.source.upper()]["alltracks"]
        import_tracks = ''
        url='https://music.yandex.ru/handlers/import.jsx'
        for item in alltracks:
            import_tracks += ' '.join(item) + '\n'
        string_of_songs=import_tracks.replace(' ','+')
        json_values={
            'content':string_of_songs
        }
        r1_import=requests.post(url,json=json_values)

        # GET
        id_import=json.loads(r1_import.text)['importCode']
        url='https://music.yandex.ru/handlers/import.jsx'
        params={
            'code':id_import
        }
        resp=requests.get(url=url, params=params)
        resp = json.loads(resp.text)
        logging.debug(f"{resp['status']}")

        while True:
            if resp['status'] == 'in-progress':
                logging.debug(f"{resp['status']}")
                time.sleep(2)
                r2_import=requests.get(url=url, params=params)
                resp = json.loads(r2_import.text)
            elif resp['status'] == 'done':
                logging.debug(f"{resp['status']}")
                trackIds = resp['trackIds']
                print(trackIds)
                break
        playlist_id, playlist_rev = self.check_playlist(f'Все треки ({self.source.upper()})')
        logging.debug(f"added 'Все треки ({self.source.upper()})'")
        for trackId in trackIds:
            self.client.users_playlists_insert_track(playlist_id, trackId.split(':')[0], trackId.split(':')[1], revision=playlist_rev)
            playlist_rev += 1
        # self.client.users_likes_tracks_add(track_ids=trackIds)



    def export_artists(self):
    # export liked artists list, skip if 'False'
        liked_artists = self.client.users_likes_artists()
        self.export_data["YM"]["artists"] = []
        for like in liked_artists:
            artist_id = like.artist.id
            artist_name = like.artist.name
            self.export_data["YM"]["artists"].append(artist_name)



    def export_albums(self):
        # export liked albums of certain artist(manually defined or ALL), skip if list is empty
        logging.debug('START export albums')
        liked_albums = self.client.users_likes_albums()
        self.export_data["YM"]["albums"] = []
        for like in liked_albums:
            if like.album.type == 'podcast':
                logging.warning(f"SKIP track with type: '{like.album.type}'")
                continue
            logging.debug(f"START export album '{like.album.title}'")
            album_title = like.album.title
            artist_name = like.album.artists[0].name
            track_count = like.album.track_count

            self.export_data['YM']['albums'].append({"title": album_title, "artist": artist_name, "tracks_count": track_count})
            logging.debug(f"DONE export album '{like.album.title}'")



    # export your playlists (manually defined or favorites), skip if list is empty
    def export_alltracks(self):
        logging.debug('START export alltracks')
        liked_tracks = self.client.users_likes_tracks().tracks
        track_count = len(liked_tracks)
        self.export_data["YM"]["alltracks"] = []
        for like in liked_tracks:
            track_title = like.track.title
            artist_name = like.track.artists[0].name
            self.export_data["YM"]["alltracks"].append([artist_name, track_title])
            logging.debug(f"{artist_name} - {track_title} OK")
        logging.debug(f"DONE export playlist 'My favorites' TOTAL: {track_count}")



    def export_playlists(self):
        my_playlists = {playlist.title: playlist.kind for playlist in self.client.users_playlists_list() if playlist}
        logging.debug('my playlists: {}'.format([item for item in my_playlists.keys()]))
        logging.debug('specified playlists: {}'.format(self.playlists_l))
        if not self.playlists_l:
            pass
        else:
            my_playlists = {key:val for key,val in my_playlists.items() if key in  self.playlists_l}
        for item, playlist_id in my_playlists.items():
            try:
                playlist = self.client.users_playlists(playlist_id)[0].tracks
            except KeyError:
                logging.error(f"FAILED TO FIND PLAYLIST '{item}'")
                continue
            self.export_data["YM"]["playlists"][item] = []
            logging.debug(f"START export playlist '{item}'")
            for like in playlist:
                if 'podcast' in like.track.type:
                    logging.warning(f"SKIP track with type: '{like.track.type}'")
                    continue
                track_title = like.track.title
                artist_name = like.track.artists[0].name
                self.export_data["YM"]["playlists"][item].append([artist_name, track_title])
                logging.debug(f"{artist_name} - {track_title} OK")
            logging.debug(f"DONE export playlist '{item}'")

