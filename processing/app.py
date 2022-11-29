import sqlite3
import connexion
from connexion import NoContent

from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from base import Base
from stats import Stats

import yaml
import logging
import logging.config
import datetime
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)

# SQLite
database = app_config["datastore"]["filename"]
url = app_config["eventstore"]["url"]
sqlite_file = app_config["datastore"]["filename"]
DB_ENGINE = create_engine(f"sqlite:///{database}")
Base.metadata.bind = DB_ENGINE
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def create_database():
    conn = sqlite3.connect(sqlite_file)

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

if os.path.exists(sqlite_file) == False:
    create_database()


def get_stats():
    # gets stats
    logger.info("GET request started")
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())

    con = sqlite3.connect(sqlite_file)
    cur = con.cursor()
    cur.execute(str(results))
    result = cur.fetchall()

    if not result:
        logger.error("No stats exist")
        return 404, "Statistics do not exist"
    else:
        stats = {
            "num_ufo_sightings": result[0][1],
            "curr_ufo_num": result[0][2],
            "num_cryptid_sightings": result[0][3],
            "curr_cryptid_num": result[0][4] 
        }
        logger.debug(stats)
    logger.info("Request has been completed")
    con.close()
    session.close()

    return stats, 200


def populate_stats():
    # populates stats in database
    logger.info("Start periodic processing")
    session = DB_SESSION()

    results = session.query(Stats).all()

    if not results:
        d = Stats(0,
                  0,
                  0,
                  0,
                  datetime.datetime.now())

        session.add(d)
        session.commit()
        session.close()

    else:
        results = session.query(Stats).order_by(Stats.last_updated.desc())

        last_updated = results[0].last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"

        num_ufo_sightings = results[0].num_ufo_sightings
        num_cryptid_sightings = results[0].num_cryptid_sightings
        curr_ufo_num = results[0].curr_ufo_num
        curr_cryptid_num = results[0].curr_cryptid_num

        ufo_req = requests.get(app_config["eventstore"]["url"] + 
                                "/UFO?timestamp=" + 
                                last_updated + "&end_timestamp=" + 
                                current_timestamp)
        if ufo_req.status_code != 200:
            logger.error("Status code for UFO events not 200")
        else:
            ufo_counter = 0
            for obj in ufo_req.json():
                num_ufo_sightings += 1
                ufo_counter += 1
                logger.debug(f"Trace ID: {obj['trace_id']}")
            logger.info(f"Number of UFO events received: {ufo_counter}")
            curr_ufo_num = ufo_counter

        cryptid_req = requests.get(app_config["eventstore"]["url"] + 
                                "/cryptid?timestamp=" + 
                                last_updated + "&end_timestamp=" + 
                                current_timestamp)
        if cryptid_req.status_code != 200:
            logger.error("Status code for cryptid events not 200")
        else:
            cryptid_counter = 0
            for obj in cryptid_req.json():
                num_cryptid_sightings += 1
                cryptid_counter += 1
                logger.debug(f"Trace ID: {obj['trace_id']}")
            logger.info(f"Number of cryptid events received: {cryptid_counter}")
            curr_cryptid_num = cryptid_counter

        current_timestamp = datetime.datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        s = Stats(num_ufo_sightings,
                curr_ufo_num,
                num_cryptid_sightings,
                curr_cryptid_num,
                current_timestamp)

        session.add(s)

        logger.debug(f"Updated statistics values: \nnum_ufo_sightings: {num_ufo_sightings} \ncurr_ufo_num: {curr_ufo_num} \nnum_cryptid_sightings: {num_cryptid_sightings} \ncurr_cryptid_num: {curr_cryptid_num}")

        session.commit()
        session.close()

        logger.info("Processing period has ended")


def init_scheduler():
    # calls populate_stats based on periodic_sec from app_conf.yml
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


def get_health():
    return 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("mysterious_sightings.yaml",
            base_path="/processing",
            strict_validation=True,
            validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run standalone get-event server
    init_scheduler()
    app.run(port=8100, use_reloader=False)