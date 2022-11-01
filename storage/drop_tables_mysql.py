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
    DROP TABLE ufo_sightings, cryptid_sightings
    ''')

db_conn.commit()
db_conn.close()