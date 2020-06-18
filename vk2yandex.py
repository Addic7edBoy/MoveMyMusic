# -*- coding: utf-8 -*-
import collections

from yandex_music.client import Client

import vk_api
from vk_api.audio import VkAudio
from config import Default
import json
import re


def get_vk(get_album=Default.GETALBUM, albums_target=Default.ALBUMS, config_filename=Default.api_config_path + 'vk_config.v2.json'):
    tracks = collections.defaultdict(lambda: collections.defaultdict(dict))
    tracks_all = []

    login, password = Default.VK_LOGIN, Default.VK_PASSWORD
    vk_session = vk_api.VkApi(login, password, config_filename=config_filename)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vkaudio = VkAudio(vk_session)

    if get_album:
        albums = vkaudio.get_albums()
        if albums_target is not None:
            albums = [album for album in albums if album['title'] in albums_target]
        print(albums)
        for album in albums:
            print(album['id'], album['title'])
            tr_list = vkaudio.get(owner_id=album['owner_id'], album_id=album['id'], access_hash=album['access_hash'])
            print(tr_list)
            for n, track in enumerate(tr_list, 1):
                artist_name = parse_artist(track['artist'].lower())
                print(artist_name)
                tracks[album['title'].lower()][artist_name][n] = track['title'].lower()

        with open(Default.VK_PATH + 'tracks_album.json', 'w', encoding='utf-8') as f:
            json.dump(tracks, f, indent=4, ensure_ascii=False)

    else:
        print('in process')
        # all_test = vkaudio.get()
        # print(type(all_test), len(all_test), type(all_test[0]), all_test[0])
        for track in vkaudio.get_iter():
            if [track['artist'].lower(), track['title'].lower()] not in tracks_all:
                tracks_all.append([track['artist'].lower(), track['title'].lower()])

        with open(Default.VK_PATH + 'tracks_all.json', 'w', encoding='utf-8') as f:
            json.dump(tracks_all, f, indent=4, ensure_ascii=False)


def parse_artist(artist_name):
    spec_symbols = re.split(', | \\.feat | feat\\. | ft | ft\\. | \\.ft| x | & ', artist_name)
    artist_name = spec_symbols[0].strip()
    return artist_name


# if __name__ == '__main__':
#     get_vk()

# https://m.vk.com/audio?act=audio_playlist-2000435640_5435640&access_hash=50f58f23977aa52f08
# https://m.vk.com/audio?act=audio_playlist-2000435640_5435640&access_hash=50f58f23977aa52f08
# https://m.vk.com/audio?act=audio_playlist147086985_76992150&access_hash=''
