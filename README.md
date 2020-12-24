Python module that helps move all your music and other stuff from one music service to another.

At this point there are 3 available platforms:
VK, Yandex.Music, Spotify

Here is a list of completed features for each service:
VK: export all music; export playlists
YM: export/import all music; export/import playlists; export albums; export favourite artists
SP: export/import all music; export/import playlists; export albums; export favourite artists



Installation:
pip install Move-My-Music

Configuration:

First of all be sure to edit config.py.example into config.py and replace essential parameteres(your login info)

There are also default parameters. You can change them either in config.py or as console arguments.

Usage:
!each parameter takes bool as input, if no parameter specified - default value will be set

parameters:
    --albums
    --alltracks
    --artists
    --playlists

to import albums and playlists from Yandex.Music to Spotify:
    moveMyMusic run -s ym -t sp --playlists True --albums True

If you want just to export data to json use 'export':
    moveMyMusic export vk --playlists True
