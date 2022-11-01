import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import random
import datetime
import json
from pykafka import KafkaClient

current_datetime = datetime.datetime.now()
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

headers = {"Content-Type": "application/json"}
# MAX_EVENTS = 10
# EVENT_FILE = "events.json"

event_data = []

def report_UFO_sighting(body):
    # receives UFO event
    python_data = json.dumps(body)
    loaded = json.loads(python_data)

    trace_id = random.randint(100000000, 999999999)
    loaded["trace_id"] = trace_id

    # logging
    logger.info(f"Received event report_UFO_sighting request with a trace id of {trace_id}")

    # requests.post("http://localhost:8090/UFO", json=loaded, headers=headers)
    # x = requests.post(app_config["eventstore1"]["url"], json=loaded, headers=headers)
    
    # logger.info(f"Returned event report_UFO_sighting response (Id: {trace_id}) with status {x.status_code}")

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = {
        "type": "ufo",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": loaded
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event report_UFO_sighting response (Id: {trace_id}) with status 201")

    # export to json
    # new_request = {"received_timestamp":"", "event":""}
    # description = loaded["description"]
    # latitude = loaded["latitude"]
    # longitude = loaded["longitude"]
    # event = f"{description} at {latitude}, {longitude}"
    
    # new_request["received_timestamp"] = current_datetime_str
    # new_request["event"] = event

    # if len(event_data) == MAX_EVENTS:
    #     event_data.pop(-1)
    #     event_data.insert(0, new_request)
    # else: 
    #     event_data.insert(0, new_request)

    # fh = open(EVENT_FILE, "w")
    # json.dump(event_data, fh)
    # fh.close()

    return NoContent, 201

def report_cryptid_sighting(body):
    # receives cryptid event
    python_data = json.dumps(body)
    loaded = json.loads(python_data)
    trace_id = random.randint(100000000, 999999999)
    loaded["trace_id"] = trace_id

    # logging
    logger.info(f"Received event report_cryptid_sighting request with a trace id of {trace_id}")

    # requests.post("http://localhost:8090/cryptid", json=loaded, headers=headers)
    # x = requests.post(app_config["eventstore2"]["url"], json=loaded, headers=headers)
    # logger.info(f"Returned event report_cryptid_sighting response (Id: {trace_id}) with status {x.status_code}")

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = {
        "type": "cryptid",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": loaded
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned event report_cryptid_sighting response (Id: {trace_id}) with status 201")

    # export to json
    # new_request = {"received_timestamp":"", "event":""}
    # description = loaded["description"]
    # latitude = loaded["latitude"]
    # longitude = loaded["longitude"]
    # event = f"{description} at {latitude}, {longitude}"
    
    # new_request["received_timestamp"] = current_datetime_str
    # new_request["event"] = event

    # if len(event_data) == MAX_EVENTS:
    #     event_data.pop(-1)
    #     event_data.insert(0, new_request)
    # else: 
    #     event_data.insert(0, new_request)

    # fh = open(EVENT_FILE, "w")
    # json.dump(event_data, fh)
    # fh.close()

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("mysterious_sightings.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)