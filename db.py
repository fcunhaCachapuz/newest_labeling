import sqlite3

conn = sqlite3.connect('weighing.sqlite')

cursor = conn.cursor()
sql_query = """ CREATE TABLE weighing (
    id text PRIMARY KEY,
    label integer NOT NULL
)"""

cursor.execute(sql_query)
