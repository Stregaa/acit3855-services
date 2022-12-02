import sqlite3
import connexion
from connexion import NoContent

from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from base import Base
from health import Health

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

# SQLite
database = app_config["datastore"]["filename"]
# url = app_config["eventstore"]["url"]
sqlite_file = app_config["datastore"]["filename"]
DB_ENGINE = create_engine(f"sqlite:///{database}")
Base.metadata.bind = DB_ENGINE
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def create_database():
    conn = sqlite3.connect(sqlite_file)

    c = conn.cursor()
    c.execute('''
            CREATE TABLE health
            (id INTEGER PRIMARY KEY ASC, 
            receiver VARCHAR(100),
            storage VARCHAR(100),
            processing VARCHAR(100),
            audit VARCHAR(100),
            last_updated VARCHAR(100) NOT NULL)
            ''')

    conn.commit()
    conn.close()

if os.path.exists(sqlite_file) == False:
    create_database()


def get_health():
    logger.info("Health check started")
    session = DB_SESSION()

    results = session.query(Health).all()

    if not results:
        h = Health("Down",
                  "Down",
                  "Down",
                  "Down",
                  datetime.datetime.now())

        session.add(h)
        session.commit()
        session.close()
    else:
        results = session.query(Health).order_by(Health.last_updated.desc())

        last_updated = results[0].last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"

        receiver = results[0].receiver
        storage = results[0].storage
        processing = results[0].processing
        audit = results[0].audit

        # health check logic
        try:
            requests.get(app_config["services"]["receiver"]["url"], timeout=5)
            receiver = "Running"
        except: 
            receiver = "Down"
        
        try:
            requests.get(app_config["services"]["storage"]["url"], timeout=5)
            storage = "Running"
        except: 
            storage = "Down"

        try:
            requests.get(app_config["services"]["processing"]["url"], timeout=5)
            processing = "Running"
        except: 
            processing = "Down"

        try:
            requests.get(app_config["services"]["audit"]["url"], timeout=5)
            audit = "Running"
        except: 
            audit = "Down"

        current_timestamp = datetime.datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        h = Health(receiver,
                  storage,
                  processing,
                  audit,
                  current_timestamp)
        
        health_dict = {
            "receiver": receiver,
            "storage": storage,
            "processing": processing,
            "audit": audit,
            "last_updated": last_updated
        }

        print(health_dict)

        session.add(h)

        logger.debug(f"Performed health check")

        session.commit()
        session.close()

        logger.info("Health check period has ended")

        return health_dict, 200


def init_scheduler():
    # calls populate_stats based on periodic_sec from app_conf.yml
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(get_health,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("mysterious_sightings.yaml",
            strict_validation=True,
            validate_responses=True)

CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run standalone get-event server
    init_scheduler()
    app.run(port=8120, use_reloader=False)