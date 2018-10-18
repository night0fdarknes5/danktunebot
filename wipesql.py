import os
import psycopg2

sql_token = os.environ.get('HEROKU_SQL_PASS')

connection = psycopg2.connect(host='ec2-107-20-141-145.compute-1.amazonaws.com', dbname='d5cejcurhdso4s', user = 'afefiqlegorfsj', password = '002f01703def828795933acbb2fa28d4d255b24d5f4a7cc9d3d9fbf1732e79c6')

cursor = connection.cursor()

cursor.execute('''SELECT * FROM "PostedSongData"''')

for row in cursor:
    print(row)


