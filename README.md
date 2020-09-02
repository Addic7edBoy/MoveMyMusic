# MoveMyMusic
python script to move playlists between music services

FATURES:

1) Export audio from VK
    |-- All tracks
    |-- All playlists
    |-- tracks + all playlists
    |-- User-defined playlists
    |-- tracks + User-defined playlists

2) Export audio from YA
    2.1) general
        All favorite artists
        All favorite albums
    2.2) music
        |-- All tracks
        |-- All playlists
        |-- tracks + all playlists
        |-- User-defined playlists
        |-- tracks + User-defined playlists
        |-- All albums
        |-- All albums + All tracks
        |-- All albums + All tracks + All playlists
        |-- All albums
        ...
3) Export Spotify
    3.1) general
        All favorite artists
    3.2)
        |-- All tracks
        |-- All playlists // Only those owned by some user (non spotify composed)
        |-- tracks + all playlists
        |-- User-defined playlists
        |-- tracks + User-defined playlists
        |-- All albums
        |-- All albums + All tracks
        |-- All albums + All tracks + All playlists
        |-- All albums
        ...

4) Import to YA
    |-- import favorite artists
    |-- import albums
    |-- import playlists
    |-- import all tracks

----IMPORT SPECIFICATIONS----
!!! import to VK is banned by owner thus not present !!!

FROM VK TO Y.MUSIC:
    import all tracks: as new playlist
    import playlists: 
                    -as new playlist
                    -as album (module checks if vk.playlist actually is an album)
 
 FROM VK TO SPOTIFY: 
    same as "vk to y music"

FROM YM TO SPOTIFY:
    import all tracks: as new playlist
    import artists: mark imported artists as favorites
    import albums: as album
    import playlists: as playlist

FROM YM TO SPOTIFY:
    same