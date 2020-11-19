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

    parser = argparse.ArgumentParser()
    # parser.prog = 'moveMyMusic'
    
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

    
    # ОБЩИЕ аргументы
    parser_model = argparse.ArgumentParser(add_help=False)
    # parser_model.set_defaults(source="file")
    # parser_model.set_defaults(target="file")
    parser_model.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP,
                            help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))


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


    # Аргументы для ЭКСПОРТА данных в файл
    export_parser = subparsers.add_parser('export', parents=[parser_base, parser_model],
                                          help='export music to json file')
    export_parser.set_defaults(phase='export')

    export_parser.add_argument('source', choices=[
                               "vk", "ym", "sp"], type=str, help='service_name to export music from')


    # Аргументы для ПОЛНОГО ПОСЛЕДОВАТЕЛЬНОГО импорта<=>экспорта
    run_parser = subparsers.add_parser('run', parents=[parser_base, parser_model],
                                          help='run full program from the beginning till the end')
    run_parser.set_defaults(phase='run')
    
    run_model.add_argument('-s', '--source', dest='source', required=True, choices=['vk', 'ym', 'sp'], type=str,
                            help='service_name to fetch music from')
    
    run_model.add_argument('-t', '--target', required=True, dest='target', choices=[
                               "ym", "sp"], type=str, help='service_name to export music to')


    # Аргументы для ИМПОРТА данных из файла
    import_parser = subparsers.add_parser('import', parents=[parser_base, parser_model],
                                          help='import music from json file')
    import_parser.set_defaults(phase='import')
    
    import_parser.add_argument('target', choices=['ym', 'sp'], type=str,
                               help='service_name to import music to')
        
    
    #ТЕСТЫ
    test_parser = subparsers.add_parser('tests', parents=[parser_base],
                                        help='import music from json file')
    test_parser.set_defaults(phase='tests')



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




    if parameters.phase == 'export' or parameters.phase == 'run':
        if parameters.source == "vk":
            vkaudio = VK.get_auth(login=parameters.vk_login,
                                  password=parameters.vk_pass, data, parameters.playlists_l)
        elif parameters.source == 'ym':
            imModel = YandexMusic(
                parameters.ym_login, parameters.ym_pass, data, playlists_l=parameters.playlists_l)
        elif parameters.source == 'sp':
            imModel = Spotify(parameters.sp_username,
                                parameters.scope, data)
        selectExport(imModel, imPhase=parameters.phase)

    elif parameters.phase == 'import':
        if parameters.target == "ym":
            imModel = YandexMusic(parameters.ym_login,
                                  parameters.ym_pass, data, source=parameters.source,
                                  playlists_l=parameters.playlists_l)
        else:
            imModel = Spotify(parameters.sp_username, parameters.scope, data, source=parameters.source)
        selectImport(imModel, imPhase=parameters.phase,
                    imSource=parameters.source, imTarget=parameters.target)



def selectImport(imModel):
    if parameters.playlists:
        imModel.import_playlists()
    if parameters.alltracks:
        imModel.import_alltracks()
    if parameters.artists:
        imModel.import_artists()
    if parameters.albums:
        imModel.import_albums()
    return "SELECT IMPORT SUCCEDED"


def selectExport(imModel, imSource, imPhase):
    if parameters.playlists:
        imModel.export_playlists()
    if parameters.alltracks:
        if imSource == 'vk':
            print('vk alltracks export unavailable')
            pass
        imModel.export_alltracks()
    if parameters.artists:
        imModel.export_artists()
    if parameters.albums:
        imModel.export_albums()
    
    data = imModel.export_data

    if imPhase == 'export':
        with open('dataTemplate.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            return "SELECT EXPORT SUCCEDED"

    status = selectImport(imModel, imPhase=parameters.phase,
                        imSource=parameters.source, imTarget=parameters.target)
    if status is not None:
        return "FULL RUN SUCCEDED"
    else:
        return "ERROR WRONG ARGUMENTS"


print('end')
if __name__ == '__main__':
    main()
