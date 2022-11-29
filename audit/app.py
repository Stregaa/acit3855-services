import connexion
from connexion import NoContent

from flask_cors import CORS, cross_origin

import json
import yaml
import logging
import logging.config
import pymysql

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

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

def get_ufo_sighting(index):
    # Get ufo sighting event in history
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to 100ms. 
    # There is a risk that this loop never stops if the index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving ufo event at index %d" % index)

    try:
        ufo_events = []
        # ufo_counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "ufo":
                ufo_events.append(msg)

        event = ufo_events[index]
        return event, 200
            
            # if msg["type"] != "ufo":
            #     continue
            # elif msg["type"] == "ufo" & ufo_counter != index:
            #     ufo_counter += 1
            # else:
            #     return msg, 200
    
    except:
        logger.error("No more messages found")

    logger.error("Could not find ufo event at index %d" % index)
    return { "message": "Not Found"}, 404


def get_cryptid_sighting(index):
    # Get cryptid sighting event in history
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving cryptid event at index %d" % index)
    try:
        cryptid_events = []
        # cryptid_counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg["type"] == "cryptid":
                cryptid_events.append(msg)

        event = cryptid_events[index]
        return event, 200

            # if msg["type"] != "cryptid":
            #     continue
            # elif msg["type"] == "cryptid" & cryptid_counter != index:
            #     cryptid_counter += 1
            # else:
            #     return msg, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find cryptid event at index %d" % index)
    return { "message": "Not Found"}, 404


def get_health():
    return 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("mysterious_sightings.yaml",
            base_path="/audit",
            strict_validation=True,
            validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8110)