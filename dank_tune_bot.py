import os
import time
import spotipy
import unicodedata
import cgi
from slackclient import SlackClient
from commands import *
from graph_handler import *
from sql_handler import *
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dank tune bots ID
BOT_ID = str(os.environ.get('SLACK_BOT_ID'))

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "yo"
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
secret_client = os.environ.get('SPOTIPY_CLIENT_SECRET') 

# instantiate Slack client and Spotify interface
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
client_credentials_manager = SpotifyClientCredentials( client_id,secret_client)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
graph = graph_handler()

songdb = sql_handler()

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = ""
    r = Commands()
    response = r.check_command(command)
    
    if response == "command1":
        songs = songdb.danktunes_posted_today()

        attach = "["
        count=True

        for item in songs:
            if count:
                attach += '''{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
                count = False
            elif not count:
                attach += ''',{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
        
        attach += "]"

        print(attach)
        
        slack_client.api_call("chat.postMessage", channel=channel, text="Dank Songs Posted Today:", as_user=True, unfurl_media=False, attachments=attach)

    elif response == "command2":
        pass

    elif response == "command3":
        songs = generate_bangers()
        
        if len(songs) == 0:
            slack_client.api_call("chat.postMessage", channel=channel, text="No Bangers left un-added", as_user=True)
            return

        attach = "["
        count=True

        for item in songs:
            if count:
                attach += '''{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
                count = False
            elif not count:
                attach += ''',{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
        
        attach += "]"

        slack_client.api_call("chat.postMessage", channel=channel, text="Bangers not added yet:", as_user=True, unfurl_media=False, attachments=attach)

    elif response == "command4":

        users = songdb.users()
        graph.create_total_post_chart(users)
        slack_client.api_call('files.upload', channels=channel, filename= "Total Posts Chart.png", file=open("./charts/Total Posts Chart.png", 'rb'))


    else:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)

def parse_slack_command_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output = slack_rtm_output

    if output and 'text' in output and AT_BOT in output['text']:
        # return text after the @ mention, whitespace removed
        return " " + output['text'].split(AT_BOT)[1].lower(), \
               output['channel']
    return None, None

def parse_song_info(data):
    """
        Takes Data imported from the slack RTM API and parses it into information to be stored. 
        Also sends a message updating the users on the amount of songs they have posted.
        Will eventually also export to an external database so Commands.py can read in 
        data and notify the group of Banger Status
    """
    songtitle = data['message']['attachments'][0]['title']
    songlink = data['message']['attachments'][0]['title_link']
    userinfo = slack_client.api_call("users.info", user = data['message']['user'])
    messagech = data['channel']
    messagets = data['message']['ts']

    track = spotify.track(songlink)
    
    songartist = track['album']['artists'][0]['name']

    if not songdb.user_exists(data['message']['user']):
        songdb.create_user({'user_id':data['message']['user'],'real_name':userinfo['user']['real_name']})
        print("User Created!")
    
    songdb.store_song_data({'ts': messagets, 'song_name': songtitle, 'song_link': songlink, 'song_artist': songartist, 'user': data['message']['user'], 'channel': messagech})

    message = "@" + userinfo['user']['name'] + " Just posted " + songtitle + " by " + songartist + "\nThis is " + str(userinfo['user']['real_name']) + "'s number " + str(songdb.user_posts_today(data['message']['user'])) + " post for today" # + songartist
    slack_client.api_call("chat.postMessage", channel=data['channel'], text=message, as_user=True, link_names=True)

def generate_bangers():
    
    bangersdb = songdb.banger_list()

    playlist = spotify.user_playlist(user = '1274812788', playlist_id = 'https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k')
    offsetno = (playlist['tracks']['total'] -100)

    if offsetno < 0:
        offsetno = 0

    bangers_and_gash = spotify.user_playlist_tracks(user = '1274812788', playlist_id = 'https://open.spotify.com/user/1274812788/playlist/3UmCrZIFWyLbWttiQPTZ9k', offset = int(offsetno))

    list = []

    for song in bangersdb:
        
        songname = song[1]
        
        for track in bangers_and_gash['items']:
            
            trackname = cgi.escape( track['track']['name'], "&")
            
            if unicodedata.normalize('NFKD', trackname).encode('ascii','ignore') == unicodedata.normalize('NFKD', songname).encode('ascii','ignore'):
                
                trackartist = track['track']['artists'][0]['name']
                songartist = song[3]
                
                if unicodedata.normalize('NFKD', trackartist).encode('ascii','ignore') == unicodedata.normalize('NFKD', songartist).encode('ascii','ignore'):
                    list.append(song)
    
    for item in list:
        bangersdb.remove(item)
    
    return bangersdb

def reaction_added(input):
        intts=int(float(input['item']['ts']))
        response = {'':''}
        response = slack_client.api_call('channels.history', channel=input['item']['channel'],latest=str(intts+1),oldest=str(intts-1),inclusive='true') #groups.history for private and channels.history for public
        if 'messages' in response:
            if 'attachments' in response['messages'][0]:
                if response['messages'][0]['attachments'][0]['service_name'] == 'Spotify':
                    if input['reaction'] != 'ear':
                        songdb.added_reaction(input['item']['ts'])

def reaction_removed(input):
    intts=int(float(input['item']['ts']))
    response = {'':''}
    response = slack_client.api_call('channels.history', channel=input['item']['channel'],latest=str(intts+1),oldest=str(intts-1),inclusive='true') #groups.history for private and channels.history for public
    if 'messages' in response:
        if 'attachments' in response['messages'][0]:
            if response['messages'][0]['attachments'][0]['service_name'] == 'Spotify':
                if input['reaction'] != 'ear':
                    songdb.removed_reaction(input['item']['ts'])                   
                                          
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("DankTuneBot connected and running!")

        input = {}
        previousinput = {}
        dailyreset = False

        while True:
            message = slack_client.rtm_read()
            if message:
                if message[0]['type'] != 'reconnect_url':
                    input = message[0]
                    print(input)

            if input and input != previousinput:
                if 'type' in input:
                    if input['type'] == "message":
                        if 'message' in input and 'attachments' in input['message']:
                            if input['message']['attachments'][0]['service_name'] == 'Spotify':
                                parse_song_info(input)
                
                
                if 'type' in input:
                    if input['type'] == "reaction_added":
                        if input['item']['type'] == 'message': 
                            if songdb.song_exists(input['item']['ts']):
                                print("Reaction Added")
                                reaction_added(input)
                
                if 'type' in input:
                    if input['type'] == "reaction_removed":
                        if input['item']['type'] == 'message': 
                            if songdb.song_exists(input['item']['ts']):
                                print("Reaction Removed")
                                reaction_removed(input)

                command, channel = parse_slack_command_output(input)

                if command and channel:
                    if message[0]['user'] != BOT_ID:
                        print("here")
                        handle_command(command, channel)
            
                previousinput = input


            if (time.time()- 49800)%86400 <= 1:
                if not dailyreset:
                    songs = songdb.danktunes_posted_today()
                    attach = "["
                    count=True
                    if len(songs) != 0:
                        for item in songs:
                            if count:
                                attach += '''{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
                                count = False
                            elif not count:
                                attach += ''',{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
        
                            attach += "]"

                            print(attach)
        
                        slack_client.api_call("chat.postMessage", channel='D5D5Z0D6H', text="Dank Songs Posted Today:", as_user=True, unfurl_media=False, attachments=attach)
                        dailyreset = True
                    else:
                        slack_client.api_call("chat.postMessage", channel='D5D5Z0D6H', text="No Dank Songs Posted Today", as_user=True)
            
            if (time.time()- 50400)%86400 <= 1:
                print("Reset")
                songdb.clear_posted_today()
                    

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
