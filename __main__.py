import VK
from config import Default
from yandexmusic import YandexMusic
from spotify import Spotify
import sys
import argparse
import json
from vk_api.audio import VkAudio
import vk_api
import sys
import distutils
from distutils import util


def str2bool(v):
    return bool(distutils.util.strtobool(v))


def process_args(args, defaults):
    """
    TESTS:
        !export all tracks VK:
        python __main__.py export 0 --alltracks true --playlists false БАН

        !export all playlists VK:
        python __main__.py export 0 --alltracks false --playlists true

        !export some playlists VK:
        python __main__.py export 0 --alltracks false --playlists true --playlists-l 'great depression' 'мои дети не будут скучать'

        !export all VK:
        python __main__.py export 0 --alltracks true --playlists true

        !export albums/artists/playlists/alltracks/all YM:
        python __main__.py export 1 --alltracks false --albums true --artists false --playlists false
        python __main__.py export 1 --alltracks false --albums false --artists true --playlists false
        python __main__.py export 1 --alltracks false --albums false --artists false --playlists true
        python __main__.py export 1 --alltracks true --albums false --artists false --playlists false
        python __main__.py export 1 --alltracks true --albums true --artists true --playlists true

        !export some playlists:
        python __main__.py export 1 --alltracks false --albums false --artists false --playlists true --playlists []
    """

    parser = argparse.ArgumentParser(description='0-vk, 1-ym, 2-sp')
    subparsers = parser.add_subparsers(title='subcommands',
                                    description='valid subcommands',
                                    help='description')
    parser.add_argument('--setup', dest='gui', type=int,
                                help='step by step setup and run')

    export_parser = subparsers.add_parser('export', help='export music to json file')
    export_parser.set_defaults(phase='export')
    export_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP, help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    export_parser.add_argument('source', choices=[0,1,2], type=int, help='service_name to export music from')
    export_parser.add_argument('--playlists', dest='playlists', type=str2bool, required=True, default=defaults.PLAYLIST, help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))
    export_parser.add_argument('--artists', dest='artists', type=str2bool, default=defaults.ARTISTS, help=('include artists as well (default: %s)' % (defaults.ARTISTS)))
    export_parser.add_argument('--albums', dest='albums', type=str2bool, default=defaults.ALBUMS, help=('include albums as well (default: %s)' % (defaults.ALBUMS)))
    export_parser.add_argument('--playlists-l', dest='playlists_l', nargs='+', default=defaults.PLAYLIST_L, help=('include albums as well (default: %s)' % (defaults.PLAYLIST_L)))
    export_parser.add_argument('--alltracks', dest='alltracks', type=str2bool, default=Default.ALLTRACKS, help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))
    # export_parser.set_defaults(func=export_only)

    import_parser = subparsers.add_parser('import', help='import music from json file')
    import_parser.set_defaults(phase='import')
    import_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP, help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    import_parser.add_argument('target', choices=[1,2], type=int,
                                help='service_name to import music to')
    import_parser.add_argument('--playlists', dest='playlists', type=str2bool, default=Default.PLAYLIST, help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))
    import_parser.add_argument('--artists', dest='artists', type=str2bool, default=defaults.ARTISTS, help=('include artists as well (default: %s)' % (defaults.ARTISTS)))
    import_parser.add_argument('--albums', dest='albums', type=str2bool, default=defaults.ALBUMS, help=('include albums as well (default: %s)' % (defaults.ALBUMS)))
    import_parser.add_argument('--playlists-l', dest='playlists_l', type=str2bool, default=defaults.PLAYLIST_L, help=('include albums as well (default: %s)' % (defaults.PLAYLIST_L)))
    import_parser.add_argument('--alltracks', dest='alltracks', type=str2bool, default=Default.ALLTRACKS, help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))
    # import_parser.set_defaults(func=import_music)
    
    parameters = parser.parse_args(args)
    return parameters


def main(args=None):
    
    if args is None:
        args = sys.argv[1:]
    print(args)
    parameters = process_args(args, Default)
    print(parameters, type(parameters))
    data_path = parameters.data_path


    try:
        with open(data_path) as f:
                data = json.load(f)
    except FileNotFoundError as e:
        print('we got: ', e.__class__)
        if parameters.phase == 'export':
            pass
        elif parameters.phase == 'import':
            print('you have nothing to import yet')
        else:
            print('make shure file_path is correct')

    if parameters.phase == 'export':
        if parameters.source == 0:
            vkaudio = VK.get_auth(login = Default.VK_LOGIN,
                                password = Default.VK_PASSWORD)
            if parameters.playlists:
                data = VK.export_playlist(vkaudio, data, parameters.playlists_l)
            if parameters.alltracks:
                tpart = VK.export_alltracks(vkaudio)
                with open('tpart.json', 'w', encoding='utf-8') as f:
                    json.dump(tpart, f, indent=4, ensure_ascii=False)

        elif parameters.source == 1:
            ym = YandexMusic(Default.YM_LOGIN, Default.YM_PASSWORD, data)
            if parameters.playlists:
                ym.export_playlists(playlists_l = parameters.playlists_l)
            if parameters.alltracks:
                ym.export_alltracks()
            if parameters.artists:
                ym.export_artists()
            if parameters.albums:
                ym.export_albums()
            data = ym.export_data
        elif parameters.source == 2:
            sp = Spotify(Default.SP_USERNAME, Default.SCOPE, data)
            if parameters.playlists:
                sp.export_playlists()
            if parameters.alltracks:
                sp.export_alltracks()
            if parameters.artists:
                sp.export_artists()
            if parameters.albums:
                sp.export_albums()
            data = sp.export_data
        with open('dataTemplate.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
    elif parameters.phase == 'import':
        if parameters.target == 1:
            pass
        elif parameters.target == 2:
            pass
    else:
        print('slomalos(')
print('end')
if __name__ == '__main__':
    main()
