import sqlite3

conn = sqlite3.connect('health.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE health
          (id INTEGER PRIMARY KEY ASC, 
           receiver VARCHAR(100) NOT NULL,
           storage VARCHAR(100) NOT NULL,
           processing VARCHAR(100) NOT NULL,
           audit VARCHAR(100) NOT NULL,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
