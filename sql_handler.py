import psycopg2
import time
import os

class sql_handler:

    sql_token = os.environ.get('HEROKU_SQL_PASS')

    ip_address = '127.0.0.1'

    db_name = 'postgres'

    sql_user = 'postgres'
    
    def update_listens(self, ts, users):

        users_formatted = users

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''UPDATE "PostedSongData" SET listened_status = (%s) WHERE ts = %s''', (users_formatted,ts))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def get_unlistened_to(self,userid):
        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()
        
        cursor.execute("BEGIN TRANSACTION")

        cursor.execute('''SELECT ts, song_name, song_link, song_artist, channel, listened_status FROM "PostedSongData"''')

        tschannel = []

        results = []

        for row in cursor:
            results.append(row)

        for row in results:
            if not userid in row[5]:
                tschannel.append([row[0],row[1], row[2], row[3], row[4],""])

        return tschannel

    def song_posted_already(self, song_title, song_artist):
        
        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()
        
        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''SELECT * FROM "PostedSongData" WHERE song_name = %s''' % ("'"+song_title+"'"))

        results = []

        for row in cursor:
            results.append(row)

        if len(results) == 0:
            connection.close()
            return False

        cursor.execute('''SELECT * FROM "PostedSongData" WHERE song_artist = %s''' % ("'"+song_artist+"'"))

        results.clear()

        for row in cursor:
            results.append(row)

        connection.close()

        if len(results) == 0:
            return False
        else:
            return True

    def get_song(self, song_name, song_artist):
        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()
        
        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''SELECT ts FROM "PostedSongData" WHERE song_name = %s AND song_artist = %s''' % ("'"+song_name+"'","'"+song_artist+"'"))

        results = []

        for row in cursor:
            results.append(row)

        ts = results[0][0]

        cursor.execute('''SELECT userid FROM "PostedSongData" WHERE song_name = %s AND song_artist = %s''' % ("'"+song_name+"'","'"+song_artist+"'"))

        results.clear()

        for row in cursor:
            results.append(row)

        userid = results[0][0]

        cursor.execute('''SELECT channel FROM "PostedSongData" WHERE song_name = %s AND song_artist = %s''' % ("'"+song_name+"'","'"+song_artist+"'"))

        results.clear()

        for row in cursor:
            results.append(row)

        channel = results[0][0]

        cursor.execute('''SELECT real_name FROM "users" WHERE user_id = %s''' % ("'"+userid+"'"))

        results.clear()

        for row in cursor:
            results.append(row)

        user_name = results[0][0]

        return user_name,ts,channel

    def store_song_data(self, songdata):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()
        
        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''INSERT INTO "PostedSongData" VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',  
                       (songdata['ts'],songdata['song_name'], songdata['song_link'],songdata['song_artist'],songdata['user'],songdata['channel'],0,"")) 

        
        cursor.execute('''SELECT songs_posted_today FROM "users" WHERE user_id = %s'''% ("'"+songdata['user']+"'"))

        songs_today = 0
        songs_alltime = 0

        for row in cursor:
            songs_today = row[0] + 1
        
        cursor.execute('''SELECT songs_posted_alltime FROM "users" WHERE user_id = %s'''% ("'"+songdata['user']+"'"))

        for row in cursor:
            songs_alltime = row[0] + 1
        
        cursor.execute('''UPDATE "users" SET songs_posted_today = %s WHERE user_id = %s '''% (songs_today,"'"+songdata['user']+"'"))

        cursor.execute('''UPDATE "users" SET songs_posted_alltime = %s WHERE user_id = %s'''% (songs_alltime,"'"+songdata['user']+"'"))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def clear_posted_today(self):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''UPDATE users SET songs_posted_today = 0''')

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def new_dank_song(self, ts):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION")

        cursor.execute('''SELECT * FROM "PostedSongData" WHERE ts=%s''', [ts])

        for row in cursor:
            songdata = row

        cursor.execute('''INSERT INTO "DankSongData" VALUES (%s,%s,%s,%s,%s,%s)''', (songdata[0],songdata[1],songdata[2],songdata[3],songdata[4],songdata[5]))

        print("Add Dank")

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def remove_dank_song(self, ts):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION")

        cursor.execute('''DELETE FROM "DankSongData" WHERE ts = %s'''%("'"+ts+"'"))

        print("Remove Dank")

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def update_reaction(self, ts, votes):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''UPDATE "PostedSongData" SET votes = (%s) WHERE ts = %s''', (votes,ts))
        print("DB Updated Reaction @ " + str(ts) + " " + str(votes))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()

    def get_reactions(self, messagets):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''SELECT votes FROM "PostedSongData" WHERE ts = %s ''' % "'"+messagets+"'")

        resultsvotes=[]

        for row in cursor:
            resultsvotes.append(row[0])

        print("DB Votes =" + str(resultsvotes[0]))
        return resultsvotes[0]

    def danktunes_posted_today(self):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

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

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "PostedSongData"''')

        results = []

        for row in cursor:
            print(row)
            if row[0] > (time.time() - period):
                results.append(row)
        return results

    def user_exists(self, userid):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

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

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

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

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute("BEGIN TRANSACTION") 

        cursor.execute('''INSERT INTO "users" VALUES (%s,%s,%s,%s)''', (userinfo['user_id'],userinfo['real_name'], 0, 0))

        cursor.execute("COMMIT TRANSACTION")

        connection.commit()

        connection.close()
    
    def user_posts_today(self, userid):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT songs_posted_today FROM public."users" WHERE user_id = %s''' % ("'"+userid+"'"))

        results = []

        for row in cursor:
            results.append(row)
        
        connection.close()

        return results[0][0]

    def banger_list(self):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)
        
        cursor = connection.cursor()

        cursor.execute('''select * FROM "DankSongData"''')

        results = []

        for row in cursor:
            results.append(row)

        connection.close()

        return results

    def users(self):

        connection = psycopg2.connect(host= self.ip_address, dbname= self.db_name, user = self.sql_user, password = self.sql_token)

        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM "users"''')

        results = []

        for row in cursor:
            results.append(row)

        return results