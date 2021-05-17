from . import VK
from .config import Default
from .yandexmusic import YandexMusic
from .spotify import Spotify
import sys
import argparse
import json
import logging
import sys
import distutils
import os
from shutil import copy2


# logging.basicConfig(filename=Default.LOG_PATH + 'running.log', filemode='w', level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# converting strings like 'False True 0 1' to bool
def str2bool(v):
    return bool(distutils.util.strtobool(v))


# проверяем остался ли поврежденный дата файл, если да - удаляем
# копируем и переименовываем файл-экземпляр
# если и он пропал я не виноват
def repair_template(path):
    if os.path.exists(path):
        os.remove(path)
        logging.debug(f"old data file ({path}) deleted")
    if not os.path.exists(str(path) + '.example'):
        logging.error(f"file 'dataTemplate.json.example' was not found")
    else:
        copy2(str(path) + '.example', str(path))
        logging.debug('example template successfully copied')
        return



# clears data file from past records
def clear_template(path=Default.DATATMP):
    logging.debug('cleaning template')
    with open(path) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as jex:
            logging.error(f"Invalid JSON response, dropping to original template \n If the problem persists, check connection to desired service")
            logging.error(jex)
            repair_template(path)
            return
        for i in data:
            for j in data[i]:
                data[i][j].clear()
        with open('dataTemplate.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data


# Parser for command-line options
def process_args(args, defaults):

    parser = argparse.ArgumentParser()
    parser.prog = 'MMM'

    parser.set_defaults(scope=defaults.SCOPE)  # область необходимых разрешений для работы со spotify API

    parser.set_defaults(data_path=defaults.DATATMP)

    parser.set_defaults(log_path=defaults.LOG_PATH)

    parser.add_argument('-s', '--source', dest='source', required=True, choices=['vk', 'ym', 'sp'], type=str,
                              help='service_name to fetch music from')

    parser.add_argument('--source-user', dest='source_user',
                              type=str, required=True, help='login for source site')

    parser.add_argument('--source-pass', dest='source_pass',
                              type=str, required=True, help='password for source site')

    parser.add_argument('-t', '--target', required=True, dest='target', choices=["ym", "sp"],
                            type=str, help='service_name to export music to')

    parser.add_argument('--target-user', dest='target_user',
                              type=str, required=True, help='login for target site')

    parser.add_argument('--target-pass', dest='target_pass',
                              type=str, required=True, help='password for target site')

    parser.add_argument('--playlists', dest='playlists',
                              action='store_true', default=defaults.PLAYLIST,
                              help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))

    parser.add_argument('--artists', dest='artists',
                              action='store_true', default=defaults.ARTISTS,
                              help=('include artists as well (default: %s)' % (defaults.ARTISTS)))

    parser.add_argument('--albums', dest='albums',
                              action='store_true', default=defaults.ALBUMS,
                              help=('include albums as well (default: %s)' % (defaults.ALBUMS)))

    parser.add_argument('--alltracks', dest='alltracks',
                              action='store_true',
                              default=defaults.ALLTRACKS,
                              help=('include albums as well (default: %s)' % (defaults.ALLTRACKS)))


    parameters = parser.parse_args(args)
    return parameters


def main(args=None):

    if args is None:
        args = sys.argv[1:]
        print(args)
    parameters = process_args(args, Default)

    if not os.path.exists(parameters.log_path):
        os.mkdir(parameters.log_path)

    logging.basicConfig(filename=parameters.log_path + 'running.log', filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    data = {
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

    if parameters.source == "vk":
        vkaudio = VK.get_auth(login=parameters.source_user,
                                password=parameters.source_pass)
        data = case_export(vkaudio,parameters, data)

        if parameters.target == "ym":
            t_obj = YandexMusic(login=parameters.target_user, password=parameters.target_pass, export_data=data, source=parameters.source)
            t_obj.get_auth()
            case_import(t_obj=t_obj, parameters=parameters)

        elif parameters.target == "sp":
            t_obj = Spotify(parameters.target_user, scope=parameters.scope,
                            data=data, source=parameters.source)
            t_obj.get_auth()
            case_import(t_obj=t_obj, parameters=parameters)

    elif parameters.source == 'ym':
        s_obj = YandexMusic(login=parameters.source_user,
                            password=parameters.source_pass, export_data=data)
        s_obj.get_auth()
        data = case_export(s_obj, parameters)
        t_obj = Spotify(parameters.target_user,
                        scope=parameters.scope, data=data, source=parameters.source)
        t_obj.get_auth()
        case_import(t_obj, parameters)

    elif parameters.source == 'sp':
        s_obj = Spotify(parameters.source_user,
                        scope=parameters.scope, data=data)
        s_obj.get_auth()
        t_obj = YandexMusic(login=parameters.target_user,
                            password=parameters.target_pass, export_data=data, source=parameters.source)
        t_obj.get_auth()
        case_import(t_obj,parameters)


# Импорт данных с учетом конфига/командных аргументов
def case_import(t_obj, parameters):
    if parameters.playlists:
        t_obj.import_playlists()
    if parameters.alltracks:
        t_obj.import_alltracks()
    if parameters.artists:
        t_obj.import_artists()
    if parameters.albums:
        t_obj.import_albums()
    return "SELECT IMPORT SUCCEDED"


def case_export(s_obj, parameters, data=None):
    if parameters.playlists:
        if parameters.source == 'vk':
            return VK.export_playlists(s_obj, data)
        else:
            s_obj.export_playlists()
    if parameters.alltracks:
        if parameters.source == 'vk':
            logging.error('vk alltracks export unavailable')    #БАГ API
            sys.exit()
        else:
            s_obj.export_alltracks()
    if parameters.artists:
        s_obj.export_artists()
    if parameters.albums:
        s_obj.export_albums()


    # извлекаем данные для всех, кроме вк. У него лишняя хромосома
    if parameters.source != 'vk':
        data = s_obj.export_data

    return data


if __name__ == '__main__':
    main()
