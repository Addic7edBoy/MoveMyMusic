# -*- coding: utf-8 -*-
import collections

from yandex_music.client import Client

from config import Default
import json
import logging


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

        playlist_new = self.client.users_playlists_create(title='Все треки (VK)')
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

    # main func for import
    def insert_yandex(self):
        with open(Default.VK_PATH + 'tracks_album.json') as f:
            tracks_album = json.load(f)

        for album in tracks_album.keys():
            if len(tracks_album[album].keys()) == 1:
                print('may be an album of curtain author')
                artist = [x for x in tracks_album[album].keys()][0]
                artist_info = self.find_artist(artist)

                if album in artist_info['artist_albums'].keys():
                    print('titles ok')
                    if len(tracks_album[album][artist].keys()) == artist_info['artist_albums'][album]['track_count']:
                        print('track count ok')
                        trigger = True
                        for export_key, export_val in tracks_album[album][artist].items():
                            if artist_info['artist_tracks'][export_val][1] == album:
                                print('track passed')
                                pass
                            else:
                                trigger = False
                                print('not same album')
                                break

                        if trigger:
                            print('full album: ', album)
                            album_id = artist_info['artist_albums'][album]['album_id']
                            self.client.users_likes_albums_add(album_ids=album_id)

            else:
                print('\n\nnot direct album, checking if playlist already created\n\n')
                # playlist_tulp = self.check_playlist(album + ' (from VK)')
                # if playlist_tulp is None:
                #     n_playlist = self.client.users_playlists_create(title=album + ' (from VK)')
                #     playlist_id = n_playlist['kind']
                #     rev = n_playlist['revision']
                #     print('\n\nMy new playlist id and revision: ', playlist_id, rev)
                # else:
                #     playlist_id, rev = playlist_tulp
                #     print('\n\nMy new playlist id and revision: ', playlist_id, rev)
                playlist_id, rev = self.check_playlist(album + ' (VK)')

                for artist, songs in tracks_album[album].items():
                    artist_info = self.find_artist(artist)
                    for song in songs.values():
                        try:
                            track_id = artist_info['artist_tracks'][str(song)][0]
                            album_id = artist_info['artist_tracks'][str(song)][2]
                            print(track_id)
                        except KeyError:
                            logging.warning(f"SEARCH FAILED '{track[0]} - {track[1]}'")
                            self.failed.append({
                                'artist': artist,
                                'song': song,
                                'available song': [artist_info['artist_tracks'].keys()]
                                })
                        else:
                            if int(track_id) in [x.id for x in self.client.users_playlists(playlist_id)[0].tracks]:
                                continue
                            else:
                                self.client.users_playlists_insert_track(
                                                                    kind=playlist_id,
                                                                    track_id=track_id,
                                                                    album_id=album_id,
                                                                    at=0,
                                                                    revision=rev)
                                rev += 1
                                logging.debug(f"'{track[-1][0]} - {track[-1][1]}' not in playlist; added")
        logging.debug('DONE')
        logging.debug(f"{len(self.failed)} couldnt be found, see more in 'failed.json'")

    def insert_all(self):
        with open(Default.VK_PATH + 'tracks_all.json') as f:
            tracks_all = json.load(f)

            # Check if playlist already exists, create if not
            # playlist_tulp = self.check_playlist('Все треки (VK)')
            # if playlist_tulp is None:
            #     playlist_new = self.client.users_playlists_create(title='Все треки (VK)')
            #     playlist_id = playlist_new['kind']
            #     rev = playlist_new['revision']
            # else:
            #     playlist_id, rev = playlist_tulp
        playlist_id, rev = self.check_playlist('Все треки (VK)')

        # Iter through tracks file and search for each
        for track in tracks_all:
            track_obj = self.client.search(
                                        text=track[0] + ' - ' + track[1],
                                        nocorrect=True,
                                        type_='track',
                                        page=0,
                                        playlist_in_best=False)
            try:
                track_title = track_obj.tracks.results[0].title
                track_id = track_obj.tracks.results[0].id
                album_id = track_obj.tracks.results[0].albums[0].id
                album_name = track_obj.tracks.results[0].albums[0].title
                artist_name = track_obj.tracks.results[0].artists[0].name
                track.append([artist_name, track_title, track_id, album_name, album_id])
            except AttributeError:
                if track_obj is None or track_obj.tracks is None:
                    logging.warning(f"SEARCH FAILED '{track[0]} - {track[1]}'")
                    self.failed.append({
                        'artist': track[0],
                        'song': track[1]
                        })
                else:
                    raise AttributeError

        # Remove failed ones
        [tracks_all.remove([fail['artist'], fail['song']]) for fail in self.failed]

        with open('tracks_all2.json', 'w', encoding='utf-8') as f:
            json.dump(tracks_all, f, indent=4, ensure_ascii=False)
        with open('failed.json', 'w', encoding='utf-8') as f:
            json.dump(self.failed, f, indent=4, ensure_ascii=False)

        # Add track to created playlist
        for track in tracks_all:
            track_id = track[-1][2]
            album_id = track[-1][-1]
            if int(track_id) in [x.id for x in self.client.users_playlists(playlist_id)[0].tracks]:
                logging.debug(f"'{track[-1][0]} - {track[-1][1]}' already in playlist")
                continue
            else:
                self.client.users_playlists_insert_track(
                                                    kind=playlist_id,
                                                    track_id=track_id,
                                                    album_id=album_id,
                                                    at=0,
                                                    revision=rev)
                rev += 1
                logging.debug(f"'{track[-1][0]} - {track[-1][1]}' not in playlist; added")
        logging.debug('DONE')
        logging.debug(f"{len(self.failed)} couldnt be found, see more in 'failed.json'")

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
                logging.debug(f"START export album '{like.album.title}',  {like.album.type}")
                continue
            logging.debug(f"START export album '{like.album.title}',  {like.album.type}")
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
            # track_album = like.track.albums[0].title
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
                    logging.debug(f"SKIP track with type: '{like.track.type}'")
                    continue
                track_title = like.track.title
                artist_name = like.track.artists[0].name
                # track_album = like.track.albums[0].title
                self.export_data["YM"]["playlists"][item].append([artist_name, track_title])
                logging.debug(f"{artist_name} - {track_title} OK")
            logging.debug(f"DONE export playlist '{item}'")
