import os
import psycopg2
import ast


input = {'messages': [{'type': 'message', 'user': 'U55SJ1H7X', 'text': '<https://open.spotify.com/track/4N3jmYazv5WPqPPRqALjwG?si=4ibsoH6xRqyl3rySTgXWpg>', 'client_msg_id': 'bf3c51e1-6a75-4fc3-896a-2d4f412b41ee', 'attachments': [{'service_name': 'Spotify', 'service_url': 'https://www.spotify.com', 'title': 'Fingers Dance', 'title_link': 'https://open.spotify.com/track/4N3jmYazv5WPqPPRqALjwG?si=4ibsoH6xRqyl3rySTgXWpg', 'thumb_url': 'https://i.scdn.co/image/16980c9eabcdd46392ff8ad0af5832e3532077ac', 'thumb_width': 640, 'thumb_height': 640, 'fallback': 'Spotify Audio: Fingers Dance', 'audio_html': '<iframe src="https://open.spotify.com/embed/track/4N3jmYazv5WPqPPRqALjwG%3Fsi%3D4ibsoH6xRqyl3rySTgXWpg" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', 'audio_html_width': 300, 'audio_html_height': 380, 'from_url': 'https://open.spotify.com/track/4N3jmYazv5WPqPPRqALjwG?si=4ibsoH6xRqyl3rySTgXWpg', 'service_icon': 'https://a.slack-edge.com/e8ef6/img/unfurl_icons/spotify.png', 'id': 1, 'original_url': 'https://open.spotify.com/track/4N3jmYazv5WPqPPRqALjwG?si=4ibsoH6xRqyl3rySTgXWpg'}], 'ts': '1540891287.004100', 'reactions': [{'name': 'ear', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': '+1', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'fire', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'hat_wobble', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'poonface', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'white_check_mark', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': '-1', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'squirrel', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'robot_face', 'users': ['U55SJ1H7X', 'U2UQ6UXNG', 'U5D3BGASW'], 'count': 3}, {'name': 'sunglasses', 'users': ['U2UQ6UXNG', 'U5D3BGASW'], 'count': 2}, {'name': 'dance', 'users': ['U2UQ6UXNG', 'U5D3BGASW'], 'count': 2}, {'name': 'datboi', 'users': ['U2UQ6UXNG', 'U5D3BGASW'], 'count': 2}]}]}

user_reactions = {}

for reaction in input['messages'][0]['reactions']:
    if reaction['name'] != "ear":
        for user in reaction['users']:
            if user_reactions.get(user) == None:
                user_reactions[user] = 1
            else:
                votes = user_reactions[user]
                user_reactions[user] = (votes + 1)

print(user_reactions['U2UQ6UXNG'])
print(len(user_reactions))