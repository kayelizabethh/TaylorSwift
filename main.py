import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import sqlalchemy

DATABASE_LOCATION = "sqlite:///taylorswift.sqlite"

# from the Spotify App Dashboard
client_id = "35e27e37584e49c9ab3b94bcfd504458"
client_secret = "db32def2f1e7471fa3f5280df77dfb36"
redirect_uri = "http://localhost:3000"

# connecting to the API
scope = "user-read-recently-played"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
))

results = spotify.current_user_recently_played()

# grabbing the albums
artist_id = "06HL4z0CvFAxyc27GXpf02"
artist = spotify.artist(artist_id)
artist_albums = spotify.artist_albums(artist['id'])


#to create the songs table
song_names = []
durations = []
track_numbers = []
album_names = []

# all of Taylor Swifts albums on Spotify
for album in artist_albums['items']:
    album_id = album['id']
    album_name = album['name']

    # filtering down the albums to remove limited edition but keep the initial (Taylor's Version) release
    if "Taylor's Version" in album_name or ("Tour" not in album_name and "(" not in album_name and len(album_name) > 3):
        artist_songs = spotify.album_tracks(album_id)['items']
        for song in artist_songs:
            song_names.append(song['name'])
            durations.append(song['duration_ms'])
            track_numbers.append(song['track_number'])
            album_names.append(album_name)

song_dictionary = {
    "track_number": track_numbers,
    "song_name": song_names,
    "duration": durations,
    "album_name": album_names
}


song_df = pd.DataFrame(song_dictionary, columns=["track_number", "song_name", "duration", "album_name"])

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('taylorswift.sqlite')
cursor = conn.cursor()


sql_query = """
   CREATE TABLE IF NOT EXISTS TaylorSwift(
       track_number INTEGER, 
       song_name VARCHAR(200),
       duration VARCHAR(200),
       album_name VARCHAR(200),
       CONSTRAINT primary_key_constraint PRIMARY KEY (song_name)
       )
   """


cursor.execute(sql_query)


try:
   song_df.to_sql("taylorswift", engine, index=False, if_exists='append')
except:
   print("Data already exists in the database")


conn.close()




