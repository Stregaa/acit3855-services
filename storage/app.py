from time import time
import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base

import yaml
import logging
import logging.config
import pymysql
import datetime
import time

from pykafka import KafkaClient
from pykafka.common import OffsetType
import json
from threading import Thread

from ufo_sightings import UFOSighting
from cryptid_sightings import CryptidSighting

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

user = app_config["datastore"]["user"]
password = app_config["datastore"]["password"]
hostname = app_config["datastore"]["hostname"]
database = app_config["datastore"]["db"]
port = app_config["datastore"]["port"]

# SQLite
# DB_ENGINE = create_engine("sqlite:///sightings.sqlite")

# MySQL
DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{database}')
Base.metadata.bind = DB_ENGINE
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f'Connecting to DB. Hostname: {hostname}, Port: {port}')

def report_UFO_sighting(body):
    # receives UFO event
    session = DB_SESSION()

    us = UFOSighting(body['description'],
                     body['latitude'],
                     body['longitude'],
                     body['number'],
                     body['shape'],
                     body['timestamp'],
                     body['trace_id'])

    session.add(us)

    # logging
    session.commit()

    logger.debug(f"Stored event report_UFO_sighting request with a trace id of {us.trace_id}")
    session.close()

    return NoContent, 201


def get_ufo_sightings(timestamp, end_timestamp):
    # receives UFO event
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    sightings = session.query(UFOSighting).filter(
        UFOSighting.date_created >= timestamp_datetime, 
        UFOSighting.date_created < end_timestamp_datetime)

    results_list = []

    for sighting in sightings:
        results_list.append(sighting.to_dict())

    session.close()

    logger.info("Query for UFO sightings after %s returns %d results" %(timestamp, len(results_list)))
    # print(results_list)
    return results_list, 200


def report_cryptid_sighting(body):
    # receives cryptid event
    session = DB_SESSION()

    cs = CryptidSighting(body['description'],
                     body['latitude'],
                     body['longitude'],
                     body['number'],
                     body['timestamp'],
                     body['trace_id'])

    session.add(cs)

    # logging
    session.commit()

    logger.debug(f"Stored event report_cryptid_sighting request with a trace id of {cs.trace_id}")
    session.close()

    return NoContent, 201


def get_cryptid_sightings(timestamp, end_timestamp):
    # receives UFO event
    # print(timestamp)
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    sightings = session.query(CryptidSighting).filter(
        CryptidSighting.date_created >= timestamp_datetime,
        CryptidSighting.date_created < end_timestamp_datetime)

    results_list = []

    for sighting in sightings:
        results_list.append(sighting.to_dict())

    session.close()

    logger.info("Query for cryptid sightings after %s returns %d results" %(timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    # Process event messages
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    retries = app_config["retries"]["max"]
    sleep_time = app_config["retries"]["sleep"]
    
    try_counter = 0

    while try_counter < retries:
        logger.info(f"Attempting to connect to Kafka - Current retry count: {try_counter}")
        try: 
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]

            # Create a consume on a consumer group, that only reads new messages
            # (uncommitted messages) when the service re-starts (i.e., it doesn't
            # read all the old messages from the history in the message queue).
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                reset_offset_on_start=False,
                                                auto_offset_reset=OffsetType.LATEST)

            # This is blocking - it will wait for a new message
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info("Message: %s" % msg)
                payload = msg["payload"]
                # print(payload)

                if msg["type"] == "ufo": # Change this to your event type
                    # Store the payload to the DB
                    report_UFO_sighting(payload)
                elif msg["type"] == "cryptid": # Change this to your event type
                    report_cryptid_sighting(payload)

                # Commit the new message as being read
                consumer.commit_offsets()

        except:
            logger.error("Connection to Kafka failed.")
            try_counter += 1
            time.sleep(sleep_time)


def get_health():
    return 200
    

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("mysterious_sightings.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)