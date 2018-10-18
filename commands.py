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
                if input.strip() == command:
                    string = command_data[command]
                    command_recognised = True
                elif not command_recognised:
                    string = "Not sure what you mean. Use the *" + "yo " + \
                        "* command with numbers, delimited by spaces."
        return string