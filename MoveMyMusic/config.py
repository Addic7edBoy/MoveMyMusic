"""
    Default parameters
    Configure parameters for preferred result.
"""
from os import environ
from dotenv import load_dotenv
load_dotenv()

class Default(object):

    SP_CLIENT_ID = environ.get('SPOTIPY_CLIENT_ID') or None
    SP_CLIENT_SECRET = environ.get('SPOTIPY_CLIENT_SECRET') or None
    SP_REDIRECT_URI = environ.get('SPOTIPY_REDIRECT_URI') or None
    SCOPE = 'user-library-modify user-library-read user-follow-read user-follow-modify playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative'

    PLAYLIST = False
    ARTISTS = False
    ALBUMS = False
    ALLTRACKS = False
    DATATMP = './dataTemplate.json'
    LOG_PATH = './logs/'
    CLEAN_PLATE = True
