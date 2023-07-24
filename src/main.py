import json
import logging
import queue
import time
import config.settings as settings

from logging.config import dictConfig
from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig
from fastapi_utils.tasks import repeat_every

from models import LogConfig
from services import LPPService, MQTTService

# globals
# queue for event processing
event_queue = queue.Queue()
error_queue = queue.Queue()
# application logging
dictConfig(LogConfig().dict())
logger = logging.getLogger("main")
# main application
app = FastAPI()
# mqtt support
mqtt_config = MQTTConfig(host=settings.MQTT_SERVER, port=settings.MQTT_PORT,
                         keepalive=settings.MQTT_KEEP_ALIVE)
mqtt = FastMQTT(config=mqtt_config)
mqtt.init_app(app)
# MQTT service
mqtt_service = MQTTService(mqtt=mqtt)
# LPP service
lpp_service = LPPService(
    url=settings.LPP_URL, timeout=settings.LPP_TIMEOUT_SEC, mqtt_service=mqtt_service)


# callback for internal MQTT connect
@mqtt.on_connect()
def connect(client, flags, rc, properties):
    logger.info(f"MQTT Connected")


# callback for internal MQTT disconnect
@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    logger.info(f"MQTT Disconnected")


# callback for all epc events
@mqtt.subscribe(settings.TOPIC_WIRAMA_EPC_ALL)
async def message_to_topic_wirama_epc_all(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    event_queue.put(payload.decode())


# callback for lpp forbidden-tags errors
@mqtt.subscribe(settings.TOPIC_LPP_STATS+'/forbidden-tags/errors/#')
async def message_to_topic_forbidden_tags_errors(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    error_queue.put(payload.decode())


# callback for lpp user-login errors
@mqtt.subscribe(settings.TOPIC_LPP_STATS+'/user-login/errors/#')
async def message_to_topic_user_login_errors(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    error_queue.put(payload.decode())


# callback for store/info
@mqtt.subscribe(settings.TOPIC_STORE_INFO)
async def message_to_topic_store_info(client, topic, payload, qos, properties):
    logger.debug(
        f"MQTT Received message to specific topic: {topic}, {payload.decode()}, {qos}, {properties}")
    try:
        json_item = json.loads(payload.decode())
        if "storeNumber" in json_item:
            settings.LOCATION_ID = json_item["storeNumber"]
        if "serialNumber" in json_item:
            settings.DEVICE_ID = json_item["serialNumber"]
        elif "doorNumber" in json_item:
            # using doorNumber as the device id for non-sfero versions
            settings.DEVICE_ID = json_item["doorNumber"]
    except Exception as err:
        logger.error(f"Unexpected {err}, {type(err)}")


# check the event queue every set schedule
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_PROCESS_EVENTS_SEC, wait_first=True)
def process_events_queue() -> None:
    try:
        epcs = []
        while not event_queue.empty():
            json_item = json.loads(event_queue.get())
            # check if EAS event type
            if "type" in json_item and json_item["type"] == "eas":
                # check if not suppressed
                if "event_type" in json_item and json_item["event_type"] != 2:
                    # capture epc
                    if "epc" in json_item:
                        epcs.append(json_item["epc"])

        if len(epcs) > 0:
            logger.info(f"{len(epcs)} epc is available")
            (forbidden, elapsed_time_ms, error) = lpp_service.forbidden_tags(epcs=epcs, deviceType=settings.DEVICE_TYPE,
                                                                      deviceId=settings.DEVICE_ID, locationId=settings.LOCATION_ID)

            # Show delayed alarm on any error https://github.com/checkpt/checkpoint-som/issues/375#issuecomment-1456215146
            if error:
                logger.warn(f"No valid response received from LPP server")
                mqtt_service.send_voice_alarm(light=settings.ALARM_DELAYED_LIGHT_ENABLE, light_color=settings.ALARM_DELAYED_LIGHT_COLOR,
                                            sound=settings.ALARM_DELAYED_SOUND_ENABLE, sound_volume=settings.ALARM_DELAYED_SOUND_VOLUME)
            # Alarm if the epc was considered forbidden
            elif forbidden:
                if elapsed_time_ms <= settings.LPP_RESPONSE_TOLERANCE_MS:
                    # Show normal alarm if less than or equal to the allowed tolerance
                    mqtt_service.send_voice_alarm(light=settings.ALARM_NORMAL_LIGHT_ENABLE, light_color=settings.ALARM_NORMAL_LIGHT_COLOR,
                                                  sound=settings.ALARM_NORMAL_SOUND_ENABLE, sound_volume=settings.ALARM_NORMAL_SOUND_VOLUME)
                else:
                    # Show delayed alarm if greater than the allowed tolerance
                    logger.warn(
                        f"LPP server response is greater than {settings.LPP_RESPONSE_TOLERANCE_MS} ms")
                    mqtt_service.send_voice_alarm(light=settings.ALARM_DELAYED_LIGHT_ENABLE, light_color=settings.ALARM_DELAYED_LIGHT_COLOR,
                                                  sound=settings.ALARM_DELAYED_SOUND_ENABLE, sound_volume=settings.ALARM_DELAYED_SOUND_VOLUME)
        else:
            # prevent high CPU usage
            time.sleep(10/1000)
    except Exception as err:
        logger.error(f"process_events_queue {err}, {type(err)}")


# refresh authentication token a minute before an hour
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_REFRESH_SEC, wait_first=False)
def authenticate_token_refresh() -> None:
    logger.info("Refreshing the authentication token...")
    try:
        lpp_service.authenticate(
            username=settings.LPP_USERNAME, password=settings.LPP_PASSWORD)
    except Exception as err:
        logger.error(f"authenticate_token_refresh {err}, {type(err)}")


# check authentication token every minute
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_AUTH_TOKEN_CHECK_SEC, wait_first=True)
def authenticate_token_check() -> None:
    logger.debug("Checking the authentication token...")
    try:
        if lpp_service.token == None:
            lpp_service.authenticate(
                username=settings.LPP_USERNAME, password=settings.LPP_PASSWORD)
    except Exception as err:
        logger.error(f"authenticate_token_check {err}, {type(err)}")


# check the error queue every set schedule and log to errors.log file
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_PROCESS_ERRORS_SEC, wait_first=True)
def process_errors_queue() -> None:
    logger.debug(f"Processing errors queue...")
    try:
        if not error_queue.empty():
            with open("./logs/errors.log", "a+") as errors_file:
                while not error_queue.empty():
                    errors_file.write(error_queue.get()+"\n")
    except Exception as err:
        logger.error(f"process_errors_queue {err}, {type(err)}")


# need to send store/info request?
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_STORE_INFO_SEC, wait_first=True)
def check_for_store_info_request() -> None:
    logger.debug(f"Checking if need to send store/info request")
    try:
        # request for the information if any of the properties were empty
        if settings.DEVICE_ID == 'EMPTY' or settings.LOCATION_ID == 'EMPTY':
            mqtt_service.send_store_info_get()
    except Exception as err:
        logger.error(f"check_for_store_info_request {err}, {type(err)}")


# inform other services to enable custom method
@app.on_event("startup")
@repeat_every(seconds=settings.SCHEDULE_CUSTOM_METHOD_SEC, wait_first=False)
def notify_custom_method() -> None:
    logger.debug(f"Checking if need to send store/info request")
    try:
        mqtt_service.send_custom_method(default_alarming=0)
    except Exception as err:
        logger.error(f"notify_custom_method {err}, {type(err)}")


# inform other services to disable custom method
@app.on_event("shutdown")
def notify_disable_custom_method() -> None:
    logger.debug(f"Sending request to disable custom method")
    try:
        mqtt_service.send_custom_method(default_alarming=1)
    except Exception as err:
        logger.error(f"notify_disable_custom_method {err}, {type(err)}")
