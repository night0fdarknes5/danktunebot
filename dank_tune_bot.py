import os
import time
import spotipy
import unicodedata
import cgi
import ast
from datetime import datetime, timezone
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
spotify_playlist = os.environ.get('SPOTIFY_PLAYLIST')

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
        
        dbinfo = []

        text = slack_client.api_call('conversations.info', channel = channel)
        if text['channel']['is_im'] == True:
            dbinfo = songdb.get_unlistened_to(text['channel']['user'])
        
        print(dbinfo)

        slack_post = []

        i = 0

        for song in dbinfo:
            link = slack_client.api_call('chat.getPermalink', channel = dbinfo[i][4], message_ts = str(dbinfo[i][0]))
            dbinfo[i][5] = link['permalink']
            i += 1

        attach = "["
        count=True
        if len(dbinfo) != 0:
            for item in dbinfo:
                if count:
                     attach += '''{"fallback": "Failed to post song.", "color": "#84bd00", "title": "Spotify Link to: %s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
                     attach += ''',{"fallback": "Failed to post song.", "color": "#f4dc42", "title": "Original Post to: %s by %s", "title_link": "%s"}'''% (item[1], item[3], item[5])
                     count = False
                elif not count:
                    attach += ''',{"fallback": "Failed to post song.", "color": "#84bd00", "title": "Spotify Link to: %s by %s", "title_link": "%s"}'''% (item[1], item[3], item[2])
                    attach += ''',{"fallback": "Failed to post song.", "color": "#f4dc42", "title": "Original Post to: %s by %s", "title_link": "%s"}'''% (item[1], item[3], item[5])
        
            attach += "]"
        
            slack_client.api_call("chat.postMessage", channel=channel, text="Unlistened to Songs:", as_user=True, unfurl_media=False, attachments=attach)
        else:
            slack_client.api_call("chat.postMessage", channel=channel, text="No Unlistened to Songs", as_user=True)

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

def parse_slack_command_output(output):
    """
        The Slack Real Time Messaging API is an events stream.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """

    if output and 'text' in output and AT_BOT in output['text']:
        # return text after the @ mention, whitespace removed
        return " " + output['text'].split(AT_BOT)[1].lower(), output['channel']
    return None, None

def parse_song_info(data):
    #    Takes Data imported from the slack RTM API and parses it into information to be stored. 
    #    Also sends a message updating the users on the amount of songs they have posted.
    #    Will eventually also export to an external database so Commands.py can read in 
    #    data and notify the group of Banger Status

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

    if not songdb.song_posted_already(songtitle, songartist):
        songdb.store_song_data({'ts': messagets, 'song_name': songtitle, 'song_link': songlink, 'song_artist': songartist, 'user': data['message']['user'], 'channel': messagech})

        message = "@" + userinfo['user']['name'] + " Just posted " + songtitle + " by " + songartist + "\nThis is " + str(userinfo['user']['real_name']) + "'s number " + str(songdb.user_posts_today(data['message']['user'])) + " post for today" # + songartist
        slack_client.api_call("chat.postMessage", channel=data['channel'], text=message, as_user=True, link_names=True)
    else:
        message = "@" + userinfo['user']['name'] + " Just posted a duplicate song " + songtitle + " by " + songartist
        slack_client.api_call("chat.postMessage", channel=data['channel'], text=message, as_user=True, link_names=True)
        user,timestamp,channel = songdb.get_song(songtitle, songartist)

        utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
        local_time = utc_time.astimezone()
        datetimestring = local_time.strftime("%H:%M on the %d/%m/%Y")

        link = slack_client.api_call('chat.getPermalink', channel = channel, message_ts = str(timestamp))
        link = link['permalink']
        
        attach = '''[{"fallback": "Failed to post song.", "color": "#84bd00", "title": "%s by %s", "title_link": "%s"}]'''% (songtitle, songartist, link)

        message = "Song was originally posted by " + user + " at " + datetimestring
        slack_client.api_call("chat.postMessage", channel=data['channel'], text=message, as_user=True, link_names=True, unfurl_media=False, attachments=attach)

def generate_bangers():
    """
    Takes a playlist and compares songs in it and songs in the database and finds songs not in the playlist in the database.
    
    """
    bangersdb = songdb.banger_list()

    playlist = spotify.user_playlist(user = '1274812788', playlist_id = spotify_playlist)
    offsetno = (playlist['tracks']['total'] -100)

    if offsetno < 0:
        offsetno = 0

    bangers_and_gash = spotify.user_playlist_tracks(user = '1274812788', playlist_id = spotify_playlist, offset = int(offsetno))

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

def reaction_changed(input):
    
    intts=int(float(input['item']['ts']))
    response = {'':''}
    response = slack_client.api_call('groups.history', channel=input['item']['channel'],latest=str(intts+1),oldest=str(intts-1),inclusive='true') #groups.history for private and channels.history for public
    
    user_reactions = {}
    user_listens = []

    if 'reactions' in response['messages'][0]:
        for reaction in response['messages'][0]['reactions']:
            if reaction['name'] != "ear":
                for user in reaction['users']:
                    if user_reactions.get(user) == None:
                        user_reactions[user] = 1

            else:
                for user in reaction['users']:
                    user_listens.append(user)

    print(user_listens)

    songdb.update_listens(input['item']['ts'],user_listens)

    db_vote = songdb.get_reactions(input['item']['ts'])

    if len(user_reactions) > db_vote:# This is when the song is upvoted
        songdb.update_reaction(input['item']['ts'],len(user_reactions))
        if len(user_reactions) == 3:
             songdb.new_dank_song(input['item']['ts'])
    elif len(user_reactions) < db_vote:# This is when the song is down voted
        songdb.update_reaction(input['item']['ts'],len(user_reactions))
        if len(user_reactions) == 2:
          songdb.remove_dank_song(input['item']['ts'])
    else:
        return

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from stream
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
                    #print(input)

            if input and input != previousinput:
                if 'type' in input:
                    if input['type'] == "message":
                        if 'message' in input and 'attachments' in input['message']:
                            if input['message']['attachments'][0]['service_name'] == 'Spotify':
                                parse_song_info(input)

                    if input['type'] == "reaction_added" or input['type'] == "reaction_removed":
                        if input['item']['type'] == 'message': 
                            if songdb.song_exists(input['item']['ts']):
                                reaction_changed(input)

                command, channel = parse_slack_command_output(input)

                if command and channel:
                    if message[0]['user'] != BOT_ID:
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
