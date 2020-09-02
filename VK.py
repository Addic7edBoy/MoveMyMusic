# -*- coding: utf-8 -*-
import collections

from yandex_music.client import Client

import vk_api
from vk_api.audio import VkAudio
from config import Default
import json
import re
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_auth(login, password):
    # init vk API session with given credentials
    vk_session = vk_api.VkApi(login, password)
    # Attempt to login into account
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        return error_msg
    logging.debug('Auth OK')
    vkaudio = VkAudio(vk_session)
    return vkaudio

def export_playlist(vkaudio, datafile, specplaylist=Default.ALBUMS):
    # Decide what we need to import
    logging.debug('GETPLAYLIST True')
    all_playlist = vkaudio.get_albums()                                                           
    if specplaylist is not None:
        logging.debug('PLAYLISTS_TARGET TRUE')
        all_playlist = [album for album in all_playlist if album['title'] in specplaylist]             # if user chose only specific playlists we check if names eq- with list comprehension
    logging.debug('get playlist tracks START')
    for item in all_playlist:
        playlist_title = item['title'].lower()        # get track list of each chosen playlist -> edit strings -> convert to dict
        datafile["VK"]["playlist"].append({playlist_title:[]})
        tr_list = vkaudio.get(owner_id=item['owner_id'], pl_id=item['id'], access_hash=item['access_hash'])
        for n, track in enumerate(tr_list, 1):
            artist_name = parse_artist(track['artist'].lower())     # delete disturbing symbols/spaces etc. cuz they'll interfere with further str. comparsion
            track_title = track['title'].lower()
            datafile["VK"]["playlist"][playlist_title].append([artist_name, track_title])
    logging.debug('get playlist tracks DONE')
    return datafile

def export_alltracks(vkaudio, datafile):
    logging.debug('GETPLAYLIST False. exporting all tracks')
    for item in vkaudio.get_iter():            # get tracklist and convert it to dict
        artist_name = parse_artist(item['artist'].lower())
        track_title = item['title'].lower()
        datafile["VK"]["alltracks"].append((artist_name, track_title))
        # if [track['artist'].lower(), track['title'].lower()] not in tracks_all:
            # tracks_all.append([track['artist'].lower(), track['title'].lower()])
    logging.debug('all tracks export DONE')
    return datafile


def validate():
    pass

def seperate_albums():
    pass

def parse_artist(artist_name):
    spec_symbols = re.split(', | \\.feat | feat\\. | ft | ft\\. | \\.ft| x | & ', artist_name)
    artist_name = spec_symbols[0].strip()
    return artist_name