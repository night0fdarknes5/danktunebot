import os
import simplejson as json

input = "yo new season https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k"

dict = {"0":""}

parsed_input = "http" + input.split("http")[1]

dict["0"] = (parsed_input)

print(dict)

with open("./playlist.json", "w+") as file:
    file.seek(0)
    json.dump(dict,file)

print("Export Complete")






#{
#  "0": "https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k"
#}
