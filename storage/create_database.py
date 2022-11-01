import sqlite3

conn = sqlite3.connect('sightings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE ufo_sightings
          (id INTEGER PRIMARY KEY ASC, 
           description VARCHAR(250) NOT NULL,
           latitude REAL NOT NULL,
           longitude REAL NOT NULL,
           number INTEGER NOT NULL,
           shape VARCHAR(100) NOT NULL,
           timestamp VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE cryptid_sightings
          (id INTEGER PRIMARY KEY ASC, 
           description VARCHAR(250) NOT NULL,
           latitude REAL NOT NULL,
           longitude REAL NOT NULL,
           number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
