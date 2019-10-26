import json
from pathlib import Path
from dateutil.relativedelta import relativedelta
from collections import defaultdict

root_path = Path("Spotify_Data")

if not root_path.exists():
    print("Please have a local copy of your spotify data in the correct location to continue")
    exit(1)

plays = []

for history_file in root_path.glob("StreamingHistory[0-9]*.json"):
    with open(history_file, 'rb') as f:
        stream_history_part = json.load(f)
        plays.extend(stream_history_part)

nonzero_plays = [x for x in plays if x["msPlayed"] != 0]
zero_plays = [x for x in plays if x["msPlayed"] == 0]
print("Number of distinct tracks played: {} ({} zero ({}%), {} nonzero ({}%))".format(len(plays), len(zero_plays), len(zero_plays) * 100 / len(plays), len(nonzero_plays), len(nonzero_plays) * 100 / len(plays)))
time_playing = sum((x["msPlayed"] for x in plays))

def humanFormatMillis(millis):
    delta = relativedelta(seconds=millis / 1000)
    delta.days
    return delta

human_time = humanFormatMillis(time_playing)
print("Number of time listened to spotify: {}".format(human_time))

# per-song analytics
# first, lets do the most listened to song
# equivalence based on name and artist, say
uniqueSongs = defaultdict(list)
for play in nonzero_plays:
    uniqueSongs[(play["artistName"], play["trackName"])].append((play["endTime"], play["msPlayed"]))

print("Unique songs played: {}".format(len(uniqueSongs)))

# title and sum of ms for each song
songsPlaytimes = [(song, sum((song_data[1] for song_data in data))) for song, data in uniqueSongs.items()]
sortedSongsPlaytimes = sorted(songsPlaytimes, key=lambda x: x[1])
for song, playtime in sortedSongsPlaytimes:
    print("{} - {} {}".format(song[0], song[1], humanFormatMillis(playtime)))

def plot_song_playtimes(songPlaytimes):
    import matplotlib.pyplot as plt
    x = range(len(songPlaytimes))
    y = [playtime for _, playtime in sortedSongsPlaytimes]
    # TODO once I have a computer that actually has a working version of numpy installed. Stupid tablet

plot_song_playtimes(sortedSongsPlaytimes)


# now lets do the same per-artist
# TODO Use pandas for this

# now lets do inference. 
# Query: how likely is it for one song to be followed by another, 
# given that it's not a playlist continuation 
# (been runing longer than, say, for one minute, and moving to the next thing on the playlist)

class Playlist:
    def __init__(self, name, modificationDate):
        self.name = name
        self.modificationDate = modificationDate
        self.entries = []

class Track:
    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album

playlists = []

for playlist_file in root_path.glob("Playlist[0-9]*.json"):
    with open(playlist_file, 'rb') as f:
        playlist_part = json.load(f)
        playlist_part = playlist_part["playlists"]
        playlist = Playlist(playlist_part["name"], playlist_part["lastModifiedDate"])
        playlist.entries = [create_track(trackDict) for trackDict in playlist[items]]
        
        


