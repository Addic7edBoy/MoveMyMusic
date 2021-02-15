"""
    Default parameters
    Configure parameters for preferred result.
"""
from os import environ
from dotenv import load_dotenv
load_dotenv()

class Default(object):

    SP_CLIENT_ID = environ.get('SP_CLIENT_ID') or None
    SP_CLIENT_SECRET = environ.get('SP_CLIENT_SECRET') or None
    SCOPE = "user-library-read user-library-modify playlist-read-private playlist-modify-private"

    PLAYLIST = False
    PLAYLIST_L = []
    ARTISTS = False
    ALBUMS = False
    ALLTRACKS = False
    DATATMP = './dataTemplate.json'
    LOG_PATH = './logs/'
    CLEAN_PLATE = True
