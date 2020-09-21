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
from timeit import default_timer as timer


def str2bool(v):
    return bool(distutils.util.strtobool(v))


def clear_template(path=Default.DATATMP):
    with open(path) as f:
        data = json.load(f)
    for i in data:
        for j in data[i]:
            data[i][j].clear()
    with open('dataTemplate.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data


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

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='description')

    parser_base = argparse.ArgumentParser(add_help=False)
    parser_base.add_argument('--log-path', dest="log_path",
                             metavar=defaults.LOG_PATH,
                             type=str, default=defaults.LOG_PATH,
                             help=('log file path (default: %s)'
                                   % (defaults.LOG_PATH)))

    parser_base.set_defaults(scope=defaults.SCOPE)
    parser_base.set_defaults(vk_login=defaults.VK_LOGIN)
    parser_base.set_defaults(vk_pass=defaults.VK_PASSWORD)
    parser_base.set_defaults(ym_login=defaults.YM_LOGIN)
    parser_base.set_defaults(ym_pass=defaults.YM_PASSWORD)
    parser_base.set_defaults(sp_username=defaults.SP_USERNAME)

    parser_model = argparse.ArgumentParser(add_help=False)

    parser_model.set_defaults(source="file")
    parser_model.set_defaults(target="file")

    parser_model.set_defaults(data_path=defaults.DATATMP)

    parser_model.add_argument('--playlists', dest='playlists', metavar=defaults.PLAYLIST,
                              type=str2bool, required=True, default=defaults.PLAYLIST,
                              help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))

    parser_model.add_argument('--artists', dest='artists', metavar=defaults.ARTISTS,
                              type=str2bool, default=defaults.ARTISTS,
                              help=('include artists as well (default: %s)' % (defaults.ARTISTS)))

    parser_model.add_argument('--albums', dest='albums', metavar=defaults.ALBUMS,
                              type=str2bool, default=defaults.ALBUMS,
                              help=('include albums as well (default: %s)' % (defaults.ALBUMS)))

    parser_model.add_argument('--playlists-l', dest='playlists_l',
                              metavar=defaults.PLAYLIST_L, nargs='+',
                              default=defaults.PLAYLIST_L,
                              help=('include albums as well (default: %s)' % (defaults.PLAYLIST_L)))

    parser_model.add_argument('--alltracks', dest='alltracks',
                              metavar=defaults.ALLTRACKS, type=str2bool,
                              default=Default.ALLTRACKS,
                              help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))

    export_parser = subparsers.add_parser('export', parents=[parser_base, parser_model],
                                          help='export music to json file')
    export_parser.set_defaults(phase='export')
    export_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP,
                               help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    export_parser.add_argument('source', choices=[
                               "vk", "ym", "sp"], type=str, help='service_name to export music from')
    export_parser.add_argument('-t', '--target', dest='target', choices=[
                               "vk", "ym", "sp"], type=str, help='service_name to export music to')

    import_parser = subparsers.add_parser('import', parents=[parser_base, parser_model],
                                          help='import music from json file')
    import_parser.set_defaults(phase='import')
    import_parser.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP,
                               help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))
    import_parser.add_argument('target', choices=['ym', 'sp'], type=str,
                               help='service_name to import music to')
    import_parser.add_argument('-s', '--source', dest='source', choices=['vk', 'ym', 'sp'], type=str,
                               help='service_name to import music to')
    test_parser = subparsers.add_parser('tests', parents=[parser_base],
                                        help='import music from json file')
    import_parser.set_defaults(phase='tests')

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
            return 'you have nothing to import yet'
        else:
            return 'make sure file_path is correct'

    if parameters.phase == 'export':
        if parameters.source == "vk":
            vkaudio = VK.get_auth(login=parameters.vk_login,
                                  password=parameters.vk_pass)
            if parameters.playlists:
                data = VK.export_playlist(
                    vkaudio, data, parameters.playlists_l)
            if parameters.alltracks:
                return 'TODO'
                # tpart = VK.export_alltracks(vkaudio)
            with open('dataTemplate.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return

        else:
            if parameters.source == 'ym':
                imModel = YandexMusic(
                    parameters.ym_login, parameters.ym_pass, data, playlists_l=parameters.playlists_l)
            elif parameters.source == 'sp':
                imModel = Spotify(parameters.sp_username,
                                  parameters.scope, data)
            if parameters.playlists:
                imModel.export_playlists()
            if parameters.alltracks:
                imModel.export_alltracks()
            if parameters.artists:
                imModel.export_artists()
            if parameters.albums:
                imModel.export_albums()
            data = imModel.export_data
            with open('dataTemplate.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            if parameters.target != 'file':
                parameters.phase = 'import'
            else:
                return

    elif parameters.phase == 'import':
        if parameters.target == "ym":
            imModel = YandexMusic(parameters.ym_login,
                                  parameters.ym_pass, data)
        elif parameters.target == "sp":
            imModel = Spotify(parameters.sp_username, parameters.scope, data)
            if parameters.playlists:
                imModel.import_playlists()
            if parameters.alltracks:
                imModel.import_alltracks()
            if parameters.artists:
                imModel.import_artists()
            if parameters.albums:
                imModel.import_albums()
    else:
        print('slomalos(')


print('end')
if __name__ == '__main__':
    main()
