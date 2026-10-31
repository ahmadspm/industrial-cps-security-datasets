import json
import os
import time
import paho.mqtt.client as mqtt
from .common import secret

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="txt-controller", protocol=mqtt.MQTTv5)
client.username_pw_set(os.environ["MQTT_USERNAME"], secret("MQTT_PASSWORD_FILE"))
client.connect(os.environ["MQTT_HOST"], 1883, 60)
client.loop_start()
for sequence in range(1, 7):
    message = json.dumps({"temperature":22.0+sequence/10,"humidity":40+sequence,"sequence":sequence,"provenance":"wire-simulated"}, separators=(",",":"))
    info = client.publish("i/bme680", message, qos=1)
    info.wait_for_publish(timeout=5)
    time.sleep(2)
client.loop_stop(); client.disconnect()
