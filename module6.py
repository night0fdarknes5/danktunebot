import os

input = "yo new season https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k"

parseduser = input.split("/user/")[1].split("/playlist/")[0]

print(parseduser)
