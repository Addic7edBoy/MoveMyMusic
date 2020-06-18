import sys
import spotipy
import spotipy.util as util
from config import Default


def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))


if __name__ == '__main__':
    # if len(sys.argv) > 1:
    #     username = sys.argv[1]
    # else:
    #     print("Whoops, need your username!")
    #     print("usage: python user_playlists.py [username]")
    #     sys.exit()
    username = Default.SP_USERNAME
    token = util.prompt_for_user_token(
                                    username,
                                    client_id=Default.SP_CLIENT_ID,
                                    client_secret=Default.SP_CLIENT_SECRET,
                                    redirect_uri='http://example.com')

    if token:
        print('token ok')
        sp = spotipy.Spotify(auth=token)
        print('spotipy ok')
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                print(playlist['name'])
                print('  total tracks', playlist['tracks']['total'])
                results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                show_tracks(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    show_tracks(tracks)
    else:
        print("Can't get token for", username)
