import json
from pathlib import Path
from dateutil.relativedelta import relativedelta

root_path = Path("Spotify_Data")

if not root_path.exists():
    print("Please have a local copy of your spotify data in the correct location to continue")
    exit(1)

plays = []

for history_file in root_path.glob("StreamingHistory[0-9]*.json"):
    with open(history_file, 'rb') as f:
        stream_history_part = json.load(f)
        plays.extend(stream_history_part)

print("Number of distinct tracks played: {}".format(len(plays)))
time_playing = sum((x["msPlayed"] for x in plays))
human_time = relativedelta(seconds=time_playing / 1000)
print("Number of time listened to spotify: {}".format(human_time))
