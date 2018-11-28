import os
import psycopg2

sql_token = os.environ.get('HEROKU_SQL_PASS')

connection = psycopg2.connect(host='127.0.0.1', dbname='postgres', user = 'postgres', password = 'password')

cursor = connection.cursor()

cursor.execute('''SELECT * FROM "PostedSongData"''')

for row in cursor:
    print(row)


