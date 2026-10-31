from __future__ import annotations

import asyncio
import json
from asyncua import Server, ua

CYCLE = [
    ("dps","workpiece_detected"),("vgr","pick_input"),("hbw","store_workpiece"),
    ("vgr","retrieve_workpiece"),("mpo","process_workpiece"),("vgr","transport_to_sld"),
    ("sld","sort_by_colour"),("vgr","deliver_output"),("dps","cycle_complete")
]

async def main() -> None:
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/factory/server/")
    server.set_server_name("Fischertechnik S7-1500 Wire Twin")
    namespace = await server.register_namespace("urn:ecu:smart-factory:plc")
    factory = await server.nodes.objects.add_object(namespace, "Factory")
    variables = {}
    for station in ("dps","vgr","hbw","mpo","sld"):
        node = await factory.add_object(namespace, station.upper())
        state = await node.add_variable(ua.NodeId(f"Factory.{station}.State", namespace), "State", "idle")
        sequence = await node.add_variable(ua.NodeId(f"Factory.{station}.Sequence", namespace), "Sequence", 0)
        variables[station] = (state, sequence)
    async with server:
        await asyncio.sleep(2)
        for number, (station, state) in enumerate(CYCLE, 1):
            await variables[station][0].write_value(state)
            await variables[station][1].write_value(number)
            print(json.dumps({"scan":number,"station":station,"state":state}))
            await asyncio.sleep(1.5)
        while True:
            await asyncio.sleep(5)

if __name__ == "__main__": asyncio.run(main())
