import VK
from .config import Default
from .yandexmusic import YandexMusic
import sys
import argparse
import json
from vk_api.audio import VkAudio
import vk_api


def process_args(args, defaults):
    parser = argparse.ArgumentParser(description='0-vk, 1-ym, 2-sp')
    subparsers = parser.add_subparsers(title='subcommands',
                                    description='valid subcommands',
                                    help='description')
    parser.add_argument('--setup', dest='gui', type=int,
                                help='step by step setup and run')

    export_parser = subparsers.add_parser('export_only', help='export music to json file')
    export_parser.set_defaults(phase='export_only')
    export_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP, help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    export_parser.add_argument('source', required=True, dest='source', choices=[0,1,2], type=int,
                                help='service_name to export music from')
    export_parser.add_argument('--include-playlists', dest='playlists', type=bool, default=defaults.PLAYLIST, help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))
    export_parser.add_argument('--include-artists', dest='artists', type=bool, default=defaults.ARTISTS, help=('include artists as well (default: %s)' % (defaults.ARTISTS)))
    export_parser.add_argument('--include-albums', dest='albums', type=bool, default=defaults.ALBUMS, help=('include albums as well (default: %s)' % (defaults.ALBUMS)))
    export_parser.add_argument('--exclude-alltracks', dest='alltracks', action="store_false",type=bool, default=defaults.ALLTRACKS, help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))
    # export_parser.set_defaults(func=export_only)

    import_parser = subparsers.add_parser('import_only', help='import music from json file')
    import_parser.set_defaults(phase='import_only')
    import_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP, help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    import_parser.add_argument('target', required=True, dest='source', choices=[1,2], type=int,
                                help='service_name to import music to')
    import_parser.add_argument('--include-playlists', dest='playlists', type=bool, default=defaults.PLAYLIST, help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))
    import_parser.add_argument('--include-artists', dest='artists', type=bool, default=defaults.ARTISTS, help=('include artists as well (default: %s)' % (defaults.ARTISTS)))
    import_parser.add_argument('--include-albums', dest='albums', type=bool, default=defaults.ALBUMS, help=('include albums as well (default: %s)' % (defaults.ALBUMS)))
    import_parser.add_argument('--exclude-alltracks', dest='alltracks', action="store_false",type=bool, default=defaults.ALLTRACKS, help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))
    # import_parser.set_defaults(func=import_music)
    
    parameters = parser.parse_args(args)
    return parameters



def main(args=None):
    
    if args is None:
        args = sys.argv[1:]
    
    parameters = process_args(args, Default)
    data_path = parameters.data_path

    with open(data_path) as f:
            data = json.load(f)

    if parameters.phase == 'export_only':
        if parameters.source == 0:
            vkaudio = VK.get_auth(login = parameters.vk_login,
                                password = parameters.vk_password)
            if parameters.playlists:
                VK.export_playlist(vkaudio, data)
            if parameters.alltracks:
                VK.export_tracks()



        elif parameters.source == 1:
            pass
        elif parameters.source == 2:
            pass
    elif parameters.phase == 'import_only':
        if parameters.target == 1:
            pass
        elif parameters.target == 2:
            pass
    else:
        print('slomalos(')

if __name__ == '__main__':
    main()
