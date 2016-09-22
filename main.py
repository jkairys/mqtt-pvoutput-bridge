import time
import logging
import copy
import pvoutput
import argparse
import json

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("config", type=str)
args = parser.parse_args()

config = args.config
if(not os.path.isfile(args.config)):
  config = (dir_path + "/" + args.config).replace("//","/")

f = open(config)
settings = json.loads(f.read())

pvoutput._api_key = settings["api_key"]
pvoutput._system_id = str(settings["system_id"])

if "min_upload_interval" in settings:
  pvoutput._min_upload_interval = settings["min_upload_interval"]

logger = logging.getLogger('mqtt-pvo')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add ch to logger
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info("MQTT To PVOutput Bridge - J. Kairys 2016")
logger.info("MQTT Server: {m}".format(m=settings["mqtt_server"]))
logger.info("MQTT Port:   {p}".format(p=settings["mqtt_port"]))
logger.info("MQTT Topic:  {t}".format(t=settings["mqtt_topic"]))
logger.info("API Key:     {k}".format(k=pvoutput._api_key))
logger.info("System ID:   {s}".format(s=pvoutput._system_id))
logger.info("Interval:    {i}s".format(i=pvoutput._min_upload_interval))
logger.info("Logging solar output to PVOutput")

import paho.mqtt.client as mqtt

ob = {
  "inverter":  {
    "ttl": None
  }
}

def on_connect(client, userdata, flags, rc):
  logger.info("MQTT connected with result code "+str(rc))
  logger.info("Subscribing to {t}".format(t=settings["mqtt_topic"]))
  client.subscribe("{t}/#".format(t=settings["mqtt_topic"]))
  logger.info("Subscribed OK.")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  pl = str(msg.payload.decode('utf-8'))
  path = msg.topic.split("/")

  if(path[0] == settings["mqtt_topic"]):
    qty = path[1]
    ob['inverter'][qty] = pl
    # wait one second for other data to arrive before sending this update
    ob['inverter']['ttl'] = 1000

  #payload = msg.payload.decode('utf-8').strip()
  #print("MQTT message: "+msg.topic+" "+str(msg.payload.decode('utf-8')))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
logger.info("Connecting to MQTT")
client.connect(settings["mqtt_server"], settings["mqtt_port"], 60)
# start background thread
client.loop_start()

logger.info("Connected to MQTT")


INTERVAL = 100
while True:
  time.sleep(INTERVAL/1000)

  if(ob["inverter"]['ttl'] is None):
    continue

  ob["inverter"]['ttl'] = ob["inverter"]['ttl'] - INTERVAL
  if ob["inverter"]['ttl'] <= 0:

    watts = ob["inverter"]["Pac1"] if "Pac1" in ob["inverter"] else None
    temp = ob["inverter"]["Tinverter"] if "Tinverter" in ob["inverter"] else None
    volts = ob["inverter"]["Vac1"] if "Vac1" in ob["inverter"] else None

    logger.info("Inverter {watts} W, {temp} *C, {volts} V".format(watts=watts, temp=temp, volts=volts))
    pvoutput.send(
      watts=watts,
      temperature=temp,
      voltage=volts
    )
    ob["inverter"]['ttl'] = None
