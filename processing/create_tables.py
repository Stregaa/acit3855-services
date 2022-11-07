import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE stats
          (id INTEGER PRIMARY KEY ASC, 
           num_ufo_sightings INTEGER NOT NULL,
           curr_ufo_num INTEGER,
           num_cryptid_sightings INTEGER NOT NULL,
           curr_cryptid_num INTEGER,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
