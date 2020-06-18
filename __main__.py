import vk2yandex
from config import Default
from yandexmusic import YandexMusic
import sys


def main(args=None):
    print('!!!MAKE SURE TO EDIT CONFIG FIRST!!!')
    print(' Choose action:')
    print('0 - From VK to Yandex.Music\n1 - From Yandex.Music to Spotify\n2 - From VK to Spotify')
    print('99 - Exit')
    x = int(input())
    if x == 0:
        vk2yandex.get_vk()
        if Default.GETALBUM:
            YandexMusic.insert_yandex()
        else:
            YandexMusic.insert_all()
    elif x == 1:
        YandexMusic.export()
    elif x == 2:
        vk2yandex.get_vk()
    elif x == 99:
        sys.exit('Exiting...')


if __name__ == '__main__':
    main()
