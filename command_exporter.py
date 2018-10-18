import os
import simplejson as json

file = open("./command_database.json", "w+")

data = {"what is your purpose?":"I pass butter.",
        "yo":"Sure...write some more code then I can do that!",
        "yo get out of here":"nah fuck off",
        "yo dank tunes today":"command1",
        "yo testing":"command2",
        "yo gimme the tunes":"command3",
        "yo stats nerd":"command4"}

file.seek(0)
file.write(json.dumps(data))