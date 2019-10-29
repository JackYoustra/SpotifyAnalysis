import json
from pathlib import Path
from dateutil.relativedelta import relativedelta
from collections import defaultdict

root_path = Path("Spotify_Data")

output_path= Path("out")

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
    y = [playtime / 1000 for _, playtime in sortedSongsPlaytimes]
    fig, ax = plt.subplots(tight_layout=True)
    ax.plot(x, y)
    ax.set(xlabel='Number of songs', ylabel='Song duration (secs)', title='Songs with time less than or equal to x')
    ax.grid()
    fig.savefig(output_path / "song_playtimes.png")

    ax.set_yscale("log")
    ax.set(xlabel='Number of songs', ylabel='Log song duration (secs)', title='Songs with time less than or equal to x')
    fig.savefig(output_path / "song_playtimes_log.png")


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

    def __str__(self):
        return "Playist {} (last modified: {}): {}".format(self.name, self.modificationDate, self.entries)
    
    def __repr__(self):
        return str(self)

class PlaylistEntry:
    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album

    def __str__(self):
        return "{} - {} ({})".format(self.title, self.artist, self.album)

    def __repr__(self):
        return str(self)

playlists = []

def create_entry(entryDict):
    trackDict = entryDict["track"]
    return PlaylistEntry(trackDict["trackName"], trackDict["artistName"], trackDict["albumName"])

for playlist_file in root_path.glob("Playlist[0-9]*.json"):
    with open(playlist_file, 'rb') as f:
        playlists_part = json.load(f)["playlists"]
        for playlist_repr in playlists_part:
            playlist = Playlist(playlist_repr["name"], playlist_repr["lastModifiedDate"])
            playlist.entries = [create_entry(trackDict) for trackDict in playlist_repr["items"]]
            playlists.append(playlist)
print(playlists) 

# Distinguish secular moves from active moves: do we move it, or not

# now let's create song durations
# a song is as long as its longest play, or a minute
# if a song plays for 

