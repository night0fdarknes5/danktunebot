import os
import simplejson as json

class Commands:
    def check_command(self, input):
        string =""
        command_recognised = False
        if os.path.isfile("./command_database.json") and os.stat("./command_database.json").st_size != 0:
            command_file = open("./command_database.json", "r+")
            command_data = json.loads(command_file.read())
        
            for command in command_data:
                if  command.lower() in input.strip().lower():
                    string = command_data[command]
                    command_recognised = True
                elif not command_recognised:
                    string = "Not sure what you mean. Use the *" + "yo " + \
                        "* command with numbers, delimited by spaces."
        return string

    def get_playlist(self):
        if os.path.isfile("./playlist.json") and os.stat("./playlist.json").st_size != 0:
            command_file = open("./playlist.json", "r+")
            command_data = json.loads(command_file.read())

        return command_data['0']

    def get_playlist_temp(self):
        if os.path.isfile("./playlist_temp.json") and os.stat("./playlist_temp.json").st_size != 0:
            command_file = open("./playlist_temp.json", "r+")
            command_data = json.loads(command_file.read())

        return command_data['0']

    def set_playlist(self):
        dict = {"0":""}

        dict["0"] = self.get_playlist_temp()

        with open("./playlist.json", "w+") as file:
            file.seek(0)
            json.dump(dict,file)
        return
        
    def set_playlist_temp(self,input):
        dict = {"0":""}

        parsed_input =  input.split("<")[1].split(">")[0]

        dict["0"] = (parsed_input)

        with open("./playlist_temp.json", "w+") as file:
            file.seek(0)
            json.dump(dict,file)
        return

    def check_admin(self,user):
        if os.path.isfile("./admins.json") and os.stat("./admins.json").st_size != 0:
            command_file = open("./admins.json", "r+")
            command_data = json.loads(command_file.read())

            for userentry in command_data:
                if command_data[userentry] == user:
                    return True

        return False