"""
    Default parameters
    Configure parameters for preferred result.
"""
import configparser
secret = configparser.ConfigParser()
secret.read("../params.ini")


class Default(object):
    def __init__():
        secret = configparser.ConfigParser()
        secret.read("../params.ini")

    # Auth VK
    VK_LOGIN = secret['VK_API']['LOGIN']      # your vk login
    VK_PASSWORD = secret['VK_API']['PASSWORD']   # your vk password
    api_config_path = '../'     # path to where session cookies are gonna be stored    !!!make sure to keep this information safe!!!

    # vk.audio export
    GETALBUM = False     # by default gets tracks, set to True if album wanted
    ALBUMS = ['Feel Alive', 'Маленькая роща деревьев дикой вишни', 'kill me plz', 'Trench']      # select which albums e.g ['my playlist1', 'my playlist2'], default None(all)

    # I/O
    VK_PATH = './'

    # Auth YANDEX MUSIC
    YM_LOGIN = secret['YM_API']['LOGIN']
    YM_PASSWORD = secret['YM_API']['PASSWORD']
    YM_TOKEN = ''

    # Yandex Music Export
    YM_ALBUMS = True     # OFF by default, select albums select which albums e.g ['playlist1', 'playlist2'], or ['ALL']
    YM_PLAYLISTS = ['H8', 'Shuffle 2']   # 'My favorites' by default, select albums select which albums e.g ['playlist1', 'playlist2'] or [] for OFF
    YM_LIKED_ARTIST = True

    # Spotify API
    SP_CLIENT_ID = secret['SP_API']['CLIENT_ID']
    SP_CLIENT_SECRET = secret['SP_API']['CLIENT_SECRET']
    SP_USERNAME = 'LittleKrishna'
