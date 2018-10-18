import psycopg2
import time
import os

class sql_handler:
    def store_song_data(self, songdata):
        
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        print(songdata['ts'])

        cursor.execute('''INSERT INTO "PostedSongData" VALUES (%s,%s,%s,%s,%s,%s,%s)''',  
                       (songdata['ts'],songdata['song_name'], songdata['song_link'],songdata['song_artist'],songdata['user'],songdata['channel'],0)) 

        
        cursor.execute('''SELECT songs_posted_today FROM "users" WHERE user_id = %s'''% ("'"+songdata['user']+"'"))

        songs_today = 0
        songs_alltime = 0

        for row in cursor:
            songs_today = row[0] + 1


        cursor.execute('''SELECT songs_posted_alltime FROM "users" WHERE user_id = %s'''% ("'"+songdata['user']+"'"))

        for row in cursor:
            songs_alltime = row[0] + 1 #this changed
        
        cursor.execute('''UPDATE "users" SET songs_posted_today = %s WHERE user_id = %s '''% (songs_today,"'"+songdata['user']+"'"))

        cursor.execute('''UPDATE "users" SET songs_posted_alltime = %s WHERE user_id = %s'''% (songs_alltime,"'"+songdata['user']+"'"))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    
    def clear_posted_today(self):

        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''UPDATE users SET songs_posted_today = 0''')

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()


    def new_dank_song(self, connection, cursor, ts):

        cursor.execute('''SELECT * FROM "PostedSongData" WHERE ts=%s''', [ts])

        for row in cursor:
            print(row)
            songdata = row


        cursor.execute('''INSERT INTO "DankSongData" VALUES (%s,%s,%s,%s,%s,%s)''', (songdata[0],songdata[1],songdata[2],songdata[3],songdata[4],songdata[5]))


    def added_reaction(self, messagets):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''SELECT votes FROM "PostedSongData"''')

        resultsvotes=[]

        for row in cursor:
            resultsvotes.append(row[0])

        cursor.execute('''SELECT ts FROM "PostedSongData"''')

        resultsts=[]

        for row in cursor:
            resultsts.append(row[0])

        votedict = {}
        n=0
        while n < len(resultsts):
            votedict[resultsts[n]] = resultsvotes[n]
            n+=1

        for ts in votedict:
            if abs(float(ts) - float(messagets)) < .0001:
                cursor.execute('''UPDATE "PostedSongData" SET (votes) = (%s) WHERE ts = %s''', ((int(votedict[ts])+1),ts))
                print("Add One @ " + str(ts) + " " + str(votedict[ts]))
                if (votedict[ts] == 2):
                    print("Add Dank")
                    self.new_dank_song(connection, cursor, ts)


        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    
    def removed_reaction(self, messagets):

        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''SELECT votes FROM "PostedSongData" WHERE ts = %s'''% ("'"+messagets+"'"))

        results = []

        for row in cursor:
            results.append(row)

        if not len(results) == 0:
            print(results[0])
            cursor.execute('''UPDATE "PostedSongData" SET votes = %s WHERE ts = %s ''', ((results[0][0]-1),messagets))
            print("Remove One @ " + messagets + " " + str(results[0][0]))

            if (results[0][0] == 3):
                print("Remove Dank")
                cursor.execute('''DELETE FROM "DankSongData" WHERE ts = %s'''%("'"+messagets+"'"))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()
        

    def danktunes_posted_today(self):

        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "DankSongData"''')

        results = []

        for row in cursor:
            if int(row[0]) > int(time.time() - ((time.time()%86400)+36000)):
                print(row)
                results.append(row)

        
        connection.close()

        return results


    def dank_songs_in_period(self, period):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "PostedSongData"''')

        results = []

        for row in cursor:
            print(row)
            if row[0] > (time.time() - period):
                results.append(row)
        return results


    def user_exists(self, userid):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "users"''')

        results = []

        for row in cursor:
            results.append(row)
            
        found = False
        
        for entry in results:
            if entry[0] == userid:
                found =True

        connection.close()

        return found


    def song_exists(self, timestamp):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "PostedSongData"''')

        results = []

        for row in cursor:
            results.append(row)
            
        found = False
        
        for entry in results:
            if str(entry[0]) == str(timestamp):
                found =True

        connection.close()

        return found


    def create_user(self, userinfo):
        
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''INSERT INTO "users" VALUES (%s,%s,%s,%s)''', (userinfo['user_id'],userinfo['real_name'], 0, 0))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    
    def user_posts_today(self, userid):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT songs_posted_today FROM public."users" WHERE user_id = %s''' % ("'"+userid+"'"))

        results = []

        for row in cursor:
            results.append(row)
        
        connection.close()

        return results[0][0]


    def banger_list(self):

        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)
        
        cursor = connection.cursor()

        cursor.execute('''select * FROM "DankSongData"''')

        results = []

        for row in cursor:
            results.append(row)

        connection.close()

        return results


    def users(self):
        sql_token = os.environ.get('HEROKU_SQL_PASS')

        connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "users"''')

        results = []

        for row in cursor:
            results.append(row)

        return results