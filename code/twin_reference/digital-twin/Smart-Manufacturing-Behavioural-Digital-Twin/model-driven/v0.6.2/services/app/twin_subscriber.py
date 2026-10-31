from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import paho.mqtt.client as mqtt
from .common import secret

evidence = Path(os.environ["EVIDENCE_PATH"])
evidence.parent.mkdir(parents=True, exist_ok=True)
revision = 0

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0: raise ConnectionError(f"MQTT connection failed: {reason_code}")
    client.subscribe([( "f/i/#", 1), ("i/#", 1)])

def on_message(client, userdata, message):
    global revision
    revision += 1
    record = {"received_at":datetime.now(timezone.utc).isoformat(),"revision":revision,"topic":message.topic,"qos":message.qos,"retain":message.retain,"payload":json.loads(message.payload),"classification":"simulated"}
    with evidence.open("a") as handle: handle.write(json.dumps(record, sort_keys=True)+"\n")
    print(json.dumps({"canonical_revision":revision,"topic":message.topic}))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="digital-twin", protocol=mqtt.MQTTv5)
client.username_pw_set(os.environ["MQTT_USERNAME"], secret("MQTT_PASSWORD_FILE"))
client.on_connect = on_connect; client.on_message = on_message
client.connect(os.environ["MQTT_HOST"], 1883, 60)
client.loop_forever()
