import pytest
from ..MoveMyMusic.yandexmusic import YandexMusic


exoport_data = {
    "YM": {
        "artists": [],
        "albums": [],
        "playlists": {},
        "alltracks": []
    },
    "SP": {
        "artists": [],
        "albums": [],
        "playlists": {},
        "alltracks": []
    },
    "VK": {
        "artists": [],
        "albums": [],
        "playlists": {},
        "alltracks": []
    }
}

import_data = {
    "YM": {
        "artists": ['ЩЕНКИ', 'Nothing but thieves', 'Muse', 'System of a down'],
        "albums": [{"title": "PAYCHECK",
                    "artist": "Пошлая Молли",
                    "tracks_count": 6},
                   {"title": "МОЯ МИЛАЯ ПУСТОТА",
                    "artist": "Pyrokinesis",
                    "tracks_count": 17},
                   {"title": "Корми демонов по расписанию",
                    "artist": "Pyrokinesis",
                    "tracks_count": 8}],
        "playlists": {},
        "alltracks": []
    },
    "SP": {
        "artists": ['ЩЕНКИ', 'Nothing but thieves', 'Muse', 'System of a down'],
        "albums": [{"title": "PAYCHECK",
                    "artist": "Пошлая Молли",
                    "tracks_count": 6},
                   {"title": "МОЯ МИЛАЯ ПУСТОТА",
                    "artist": "Pyrokinesis",
                    "tracks_count": 17},
                   {"title": "Корми демонов по расписанию",
                    "artist": "Pyrokinesis",
                    "tracks_count": 8}],
        "playlists": {},
        "alltracks": []
    },
    "VK": {
        "artists": [],
        "albums": [],
        "playlists": {},
        "alltracks": []
    }
}

login = xxx
password = xxx


def test_export_all():
    ym_obj = YandexMusic(login=login, password=password, export_data=exoport_data)
    ym_obj.get_auth()
    ym_obj.export_alltracks()
    out = ym_obj.export_data
    print(len(out["YM"]["alltracks"]))
    print(out["YM"]["alltracks"][:2])

def test_get_playlists():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=exoport_data)
    ym_obj.get_auth()
    out = ym_obj.get_playlists()
    print(out)

def test_export_playlists_all():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=exoport_data)
    ym_obj.get_auth()
    ym_obj.export_playlists()
    out = ym_obj.export_data
    print(len(out["YM"]["playlists"]))


def test_export_playlists():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=exoport_data)
    ym_obj.get_auth()
    ym_obj.export_playlists(playlist_chosen=None)
    out = ym_obj.export_data
    print(len(out["YM"]["playlists"]))


def test_export_albums():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=exoport_data)
    ym_obj.get_auth()
    ym_obj.export_albums()
    out = ym_obj.export_data
    print(len(out["YM"]["albums"]))
    print(out["YM"]["albums"][:2])

def test_export_artists():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=exoport_data)
    ym_obj.get_auth()
    ym_obj.export_artists()
    out = ym_obj.export_data
    print(len(out["YM"]["artists"]))
    print(out["YM"]["artists"][:2])


def test_import_all():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=import_data, source='sp')
    ym_obj.get_auth()
    ym_obj.import_alltracks()



def test_import_playlists():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=import_data, source='sp')
    ym_obj.get_auth()
    ym_obj.import_playlists()



def test_import_albums():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=import_data, source='sp')
    ym_obj.get_auth()
    ym_obj.import_albums()



def test_import_artists():
    ym_obj = YandexMusic(login=login,
                         password=password, export_data=import_data, source='sp')
    ym_obj.get_auth()
    ym_obj.import_artists()
