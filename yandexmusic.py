# -*- coding: utf-8 -*-
import collections

from yandex_music.client import Client

from .config import Default
import json
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('yandex_music').setLevel(logging.ERROR)


class YandexMusic(object):
    def __init__(self):
        self.failed = []
        self.my_id = None
        self.login = Default.YM_LOGIN
        self.password = Default.YM_PASSWORD
        self.client = Client.from_credentials(self.login, self.password)
        self.export_artist = Default.YM_LIKED_ARTIST
        self.export_album = Default.YM_ALBUMS
        self.export_playlist = Default.YM_PLAYLISTS
        self.export_data = collections.defaultdict(dict)

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
                    artist_info = self.find_artist(artist, self.client)
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

    def export(self):

        # export liked artists list, skip if 'False'
        if self.export_artist:
            liked_artists = self.client.users_likes_artists()
            for like in liked_artists:
                artist_id = like.artist.id
                artist_name = like.artist.name
                self.export_data['artists'][artist_name] = artist_id
            print(self.export_data)

        # export liked albums of certain artist(manually defined or ALL), skip if list is empty
        if self.export_album:
            logging.debug('START export albums')
            liked_albums = self.client.users_likes_albums()
            for like in liked_albums:
                logging.debug(f"START export album '{like.album.title}'")
                album_title = like.album.title
                artist_name = like.album.artists[0].name
                track_count = like.album.track_count
                self.export_data['albums'][str(album_title + ' - ' + artist_name)] = [volume.title for volume in like.album.with_tracks().volumes[0]]
                logging.debug(f"DONE export album '{like.album.title}'")
            logging.debug(f"DONE export albums'{like.album.title}'")

        # export your playlists (manually defined or favorites), skip if list is empty
        if self.export_playlist:
            logging.debug('START export playlists')
            if len(self.export_playlist) == 1 and self.export_playlist[0] == 'My favorites':
                liked_tracks = self.client.users_likes_tracks().tracks
                self.export_data['playlist']['My favorites'] = []
                for like in liked_tracks:
                    track_title = like.track.title
                    artist_name = like.track.artists[0].name
                    track_album = like.track.albums[0].title
                    self.export_data['playlist']['My favorites'].append([artist_name, track_title, track_album])
                logging.debug(f"DONE export playlist 'My favorites'")
            else:
                my_playlists = {playlist.title: playlist.kind for playlist in self.client.users_playlists_list()}
                for item in self.export_playlist:
                    logging.debug(f"START export playlist '{item}'")
                    try:
                        playlist_id = my_playlists[item]
                        playlist = self.client.users_playlists(playlist_id)[0].tracks
                    except KeyError:
                        logging.error(f"FAILED TO FIND PLAYLIST '{item}'")
                        continue
                    self.export_data['playlist'][item] = []
                    for like in playlist:
                        track_title = like.track.title
                        artist_name = like.track.artists[0].name
                        track_album = like.track.albums[0].title
                        self.export_data['playlist'][item].append([artist_name, track_title, track_album])
                    logging.debug(f"DONE export playlist '{item}'")
        with open('export_YM.json', 'w', encoding='utf-8') as f:
            json.dump(self.export_data, f, indent=4, ensure_ascii=False)


# if __name__ == '__main__':
#     YM = YandexMusic()
#     YM.export()
