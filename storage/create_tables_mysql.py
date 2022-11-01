import mysql.connector
import yaml

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

user = app_config["datastore"]["user"]
password = app_config["datastore"]["password"]
hostname = app_config["datastore"]["hostname"]
database = app_config["datastore"]["db"]

db_conn = mysql.connector.connect(host=hostname, user=user, password=password, database=database)

db_cursor = db_conn.cursor()
db_cursor.execute('''
    CREATE TABLE ufo_sightings
    (id INT NOT NULL AUTO_INCREMENT,
    description VARCHAR(250) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    number INT NOT NULL,
    shape VARCHAR(100) NOT NULL,
    timestamp VARCHAR(100) NOT NULL,
    date_created VARCHAR(100) NOT NULL,
    trace_id INT NOT NULL,
    CONSTRAINT ufo_sighting_pk PRIMARY KEY (id))
    ''')

db_cursor.execute('''
    CREATE TABLE cryptid_sightings
    (id INT NOT NULL AUTO_INCREMENT,
    description VARCHAR(250) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    number INT NOT NULL,
    timestamp VARCHAR(100) NOT NULL,
    date_created VARCHAR(100) NOT NULL,
    trace_id INT NOT NULL,
    CONSTRAINT cryptid_sighting_pk PRIMARY KEY (id))
    ''')

db_conn.commit()
db_conn.close()