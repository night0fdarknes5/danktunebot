#import psycopg2
#import time


#cursor = connection.cursor()

#cursor.execute("BEGIN TRANSACTION") 

#cursor.execute('''CREATE TABLE "PostedSongData" (ts numeric, song_name text, song_link text, song_artist text, userid text, channel text, votes integer)''')

#cursor.execute('''CREATE TABLE "DankSongData" (ts numeric, song_name text, song_link text, song_artist text, userid text, channel text)''')

#cursor.execute('''CREATE TABLE "users" (user_id text, real_name text, songs_posted_today integer, songs_posted_alltime integer)''')

#cursor.execute("COMMIT TRANSACTION")

#connection.commit()

#connection.close()

#print("Transaction Complete")

import matplotlib.pyplot as plt

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
sizes = [15, 30, 30, 25]
explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.savefig('./charts/totalpostchart.png', bbox_inches='tight')
