from __future__ import annotations

import asyncio
import json
import os
from asyncua import Client
import paho.mqtt.client as mqtt
from .common import TOPICS, secret

class Handler:
    def __init__(self, mqtt_client: mqtt.Client): self.mqtt = mqtt_client
    def datachange_notification(self, node, value, data):
        node_id = node.nodeid.Identifier
        if not str(node_id).endswith(".State"): return
        station = str(node_id).split(".")[1]
        topic = "f/i/state/dso" if station == "dps" and value == "cycle_complete" else TOPICS[station]
        message = json.dumps({"station":station,"state":value,"source":"opcua","provenance":"wire-simulated"}, separators=(",",":"))
        info = self.mqtt.publish(topic, message, qos=1, retain=True)
        info.wait_for_publish(timeout=5)
        print(json.dumps({"bridge":"opcua-to-mqtt","node":node_id,"topic":topic,"state":value}))

async def main() -> None:
    mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-gateway", protocol=mqtt.MQTTv5)
    mq.username_pw_set(os.environ["MQTT_USERNAME"], secret("MQTT_PASSWORD_FILE"))
    mq.connect(os.environ["MQTT_HOST"], 1883, 60)
    mq.loop_start()
    try:
        async with Client(os.environ["OPCUA_ENDPOINT"]) as ua_client:
            subscription = await ua_client.create_subscription(250, Handler(mq))
            namespace = await ua_client.get_namespace_index("urn:ecu:smart-factory:plc")
            nodes = [ua_client.get_node(f"ns={namespace};s=Factory.{station}.State") for station in TOPICS]
            await subscription.subscribe_data_change(nodes)
            while True: await asyncio.sleep(2)
    finally:
        mq.loop_stop(); mq.disconnect()

if __name__ == "__main__": asyncio.run(main())
