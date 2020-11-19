import VK
from config import Default
from yandexmusic import YandexMusic
from spotify import Spotify
import sys
import argparse
import json
from vk_api.audio import VkAudio
import logging
import vk_api
import sys
import distutils
from distutils import util
from timeit import default_timer as timer
import os
from shutil import copy2


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
        # os.rename(str(path)+'.example', path)
    


# clears data file from past records
def clear_template(path=Default.DATATMP):
    with open(path) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as jex:
            logging.error(f"Invalid JSON response, dropping to original template \n If the problem persists, check connection to desired service")
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
    # parser.prog = 'moveMyMusic'
    
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='description')
    
    parser_base = argparse.ArgumentParser(add_help=False)

    parser_base.set_defaults(scope=defaults.SCOPE)  # область необходимых разрешений для работы со spotify API
    parser_base.set_defaults(vk_login=defaults.VK_LOGIN)
    parser_base.set_defaults(vk_pass=defaults.VK_PASSWORD)
    parser_base.set_defaults(ym_login=defaults.YM_LOGIN)
    parser_base.set_defaults(ym_pass=defaults.YM_PASSWORD)
    parser_base.set_defaults(sp_username=defaults.SP_USERNAME)

    parser_base.add_argument('--log-path', dest="log_path",
                             metavar=defaults.LOG_PATH,
                             type=str, default=defaults.LOG_PATH,
                             help=('log file path (default: %s)'
                                   % (defaults.LOG_PATH)))

    
    # ОБЩИЕ аргументы
    parser_model = argparse.ArgumentParser(add_help=False)
    parser_model.add_argument('--data-path', dest='data_path', type=str, default=defaults.DATATMP,
                            help=('path+filename to data template(default: %s)' % (defaults.DATATMP)))


    parser_model.set_defaults(data_path=defaults.DATATMP)

    parser_model.add_argument('--playlists', dest='playlists', metavar=defaults.PLAYLIST,
                              type=str2bool, required=True, default=defaults.PLAYLIST,
                              help=('include playlists as well (default: %s)' % (defaults.PLAYLIST)))

    parser_model.add_argument('--clean-plate', dest='clean_plate',
                                action='store_true', default=defaults.CLEAN_PLATE,
                                help='Delete all past records in dataTemplate')

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
    
    run_parser.add_argument('-s', '--source', dest='source', required=True, choices=['vk', 'ym', 'sp'], type=str,
                            help='service_name to fetch music from')
    
    run_parser.add_argument('-t', '--target', required=True, dest='target', choices=[
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

    # Проверяем существует ли дата файл и наличие содержимого
    # Таким образом пресекаем импорт до первого экспорта
    try:
        with open(data_path) as f:
            if parameters.clean_plate:
                clear_template(data_path)
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
                                  password=parameters.vk_pass)

            # Сразу вызываем экспорт плейлиста, так как вк кал и больше ничего нельзя
            selectExport(imModel=vkaudio, imPhase=parameters.phase,
                        parameters=parameters, imSource=parameters.source, datafile=data)
        
        elif parameters.source == 'ym':
            imModel = YandexMusic(
                parameters.ym_login, parameters.ym_pass, data, playlists_l=parameters.playlists_l)
            selectExport(imModel, imPhase=parameters.phase, parameters=parameters)

        elif parameters.source == 'sp':
            imModel = Spotify(parameters.sp_username,
                                parameters.scope, data)
            selectExport(imModel, imPhase=parameters.phase, parameters=parameters)

    elif parameters.phase == 'import':
        if parameters.target == "ym":
            imModel = YandexMusic(parameters.ym_login,
                                  parameters.ym_pass, data, source=parameters.source,
                                  playlists_l=parameters.playlists_l)
        else:
            imModel = Spotify(parameters.sp_username, parameters.scope, data, source=parameters.source)
        selectImport(imModel, parameters)


# Импорт данных с учетом конфига/командных аргументов
def selectImport(imModel, parameters):
    if parameters.playlists:
        imModel.import_playlists()
    if parameters.alltracks:
        imModel.import_alltracks()
    if parameters.artists:
        imModel.import_artists()
    if parameters.albums:
        imModel.import_albums()
    return "SELECT IMPORT SUCCEDED"


# Экспорт данных с учетом конфига/командных аргументов
# Фазы экспорта и полного пробега начинаются в одной точке
# При экспорте данные просто пишутся в файл
# При выполнении всей программы (run) последовательно выполняется сначала экспорт из выбранной платформы,
# сразу за ним вызывается импорт на целевую платформу (selectImport)
# В качестве выхода - строка результат выполнения
# imModel - с API какого сервиса работаем в данный момент [vk,sp,ym]
# imSource - Откуда берем музыку ---> записывается в файл
# imPhase - Какую часть кода выполнять:
#                                   [export - получаение данных и запись,
#                                   import - чтение данных их применение,
#                                   run - получение => применение]

def selectExport(imModel, imPhase, parameters, imSource=None, datafile=None):
    if parameters.playlists:
        if imSource == 'vk':
            data = VK.export_playlists(imModel, datafile, parameters.playlists_l)
        else:
            imModel.export_playlists()
    if parameters.alltracks:
        if imSource == 'vk':
            logging.error('vk alltracks export unavailable')
            sys.exit()
        else:
            imModel.export_alltracks()
    if parameters.artists:
        imModel.export_artists()
    if parameters.albums:
        imModel.export_albums()


    # извлекаем данные для всех, кроме вк. У него лишняя хромосома
    if imSource != 'vk':
        data = imModel.export_data


    # Если задача экспорта - пишем в файл и останавливаемся
    # В противном случае (run) сразу начинаем импорт
    # на всякий случай возвращаем статус выполнения каждого шага
    if imPhase == 'export':
        with open('dataTemplate.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            return "SELECT EXPORT SUCCEDED"
    else:
        status = selectImport(imModel, parameters)
        if status is not None:
            return "FULL RUN SUCCEDED"
        else:
            return "ERROR WRONG ARGUMENTS"

logging.debug('END.')

if __name__ == '__main__':
    main()
