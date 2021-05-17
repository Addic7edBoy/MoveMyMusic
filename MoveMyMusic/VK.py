    # -*- coding: utf-8 -*-
import collections

from yandex_music.client import Client

import vk_api
from vk_api.audio import VkAudio
from .config import Default
import json
import re
import logging

# logging.basicConfig(level=logging.DEBUG,
                    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_auth(login, password):
    # init vk API session with given credentials
    # logging.debug(login, type(login), password, type(password))
    vk_session = vk_api.VkApi(login, password)
    # Attempt to login into account
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        logging.error('Two factor auth needed. If you have it on purpose - disable. \n Otherwise try waiting some time')
        return error_msg
    logging.debug('Auth OK')
    vkaudio = VkAudio(vk_session)
    return vkaudio


def get_playlists(vkaudio):
    return vkaudio.get_albums()


def export_playlists(vkaudio, datafile, playlist_chosen=None):
    # Decide what we need to import
    logging.debug('GETPLAYLIST True')
    if playlist_chosen:
        all_playlist = playlist_chosen
    else:
        all_playlist = get_playlists(vkaudio)

    logging.debug('get playlist tracks START')
    for item in all_playlist:
        playlist_title = item['title'].lower()        # get track list of each chosen playlist -> edit strings -> convert to dict
        logging.debug('GET PLAYLIST: {}'.format(playlist_title))
        datafile["VK"]["playlists"][playlist_title] = []
        tr_list = vkaudio.get(owner_id=item['owner_id'], album_id=item['id'], access_hash=item['access_hash'])
        for n, track in enumerate(tr_list, 1):
            artist_name = parse_artist(track['artist'].lower())     # delete disturbing symbols/spaces etc. cuz they'll interfere with further str. comparsion
            track_title = track['title'].lower()
            datafile["VK"]["playlists"][playlist_title].append([artist_name, track_title])
            logging.debug('     +{0} - {1}'.format(artist_name, track_title))
        logging.debug('PLAYLIST TOTAL: {}'.format(len(datafile["VK"]["playlists"][playlist_title])))
    logging.debug('get playlist tracks DONE')
    return datafile


# СУКИ ВСЁ СЛОМАЛИ НИЧЕ НЕ РАБОТАЕТ(
def export_alltracks(vkaudio, datafile):
    data = []
    logging.debug('GETPLAYLIST False. exporting all tracks')
    for item in vkaudio.get():            # get tracklist and convert it to dict
        artist_name = parse_artist(item['artist'].lower())
        track_title = item['title'].lower()
        logging.debug(track_title)
        data.append([artist_name, track_title])
    logging.debug('all tracks export DONE. stats: list of list - {0}'.format(len(data)))
    return data




def parse_artist(artist_name):
    spec_symbols = re.split(', | \\.feat | feat\\. | ft | ft\\. | \\.ft| x | & ', artist_name)
    artist_name = spec_symbols[0].strip()
    return artist_name
