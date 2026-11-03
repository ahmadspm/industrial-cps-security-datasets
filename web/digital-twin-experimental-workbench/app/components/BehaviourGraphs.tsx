"use client";

import {
  Background,
  Controls,
  Edge,
  MarkerType,
  Node,
  ReactFlow,
} from "@xyflow/react";

const COLORS = [
  "#2476c9",
  "#7358c3",
  "#d18a26",
  "#d14d43",
  "#168b72",
  "#397d51",
];
const stationStates: Record<string, string[]> = {
  DSI: ["IDLE", "DETECT", "IDENTIFY", "REQUEST", "RELEASE"],
  VGR: ["IDLE", "REFERENCE", "PICK", "TRANSPORT", "PLACE", "RETURN"],
  HBW: ["IDLE", "IDENTIFY", "STORE", "RESERVED", "RETRIEVE"],
  MPO: ["IDLE", "LOAD", "OVEN", "TRANSFER", "SAW", "EJECT"],
  SLD: ["IDLE", "DETECT", "CLASSIFY", "EJECT", "CONFIRM"],
  DSO: ["IDLE", "WAIT", "DETECT", "COMPLETE"],
};

function ellipse(label: string, index: number, active: boolean) {
  return (
    <div
      className={`ellipse-node ${active ? "active" : ""}`}
      style={
        { "--ellipse": COLORS[index % COLORS.length] } as React.CSSProperties
      }
    >
      <b>{label}</b>
      <span>{active ? "CURRENT STATE" : `S${index}`}</span>
    </div>
  );
}

export function StateMachineGraph({
  station,
  tick,
}: {
  station: string;
  tick: number;
}) {
  const states = stationStates[station] || stationStates.VGR;
  const active = tick % states.length;
  const center = { x: 340, y: 170 },
    radiusX = 300,
    radiusY = 145;
  const nodes: Node[] = states.map((s, i) => {
    const angle = -Math.PI / 2 + (i * Math.PI * 2) / states.length;
    return {
      id: s,
      position: {
        x: center.x + Math.cos(angle) * radiusX,
        y: center.y + Math.sin(angle) * radiusY,
      },
      data: { label: ellipse(s, i, i === active) },
      style: { width: 150, border: 0, background: "transparent", padding: 0 },
    };
  });
  nodes.push({
    id: "fault",
    position: { x: 340, y: 170 },
    data: { label: ellipse("FAULT", 5, false) },
    style: { width: 150, border: 0, background: "transparent", padding: 0 },
  });
  const edges: Edge[] = [];
  states.forEach((s, i) =>
    edges.push({
      id: `${s}-${i}`,
      source: s,
      target: states[(i + 1) % states.length],
      label: i === states.length - 1 ? "reset" : "event / guard",
      type: "smoothstep",
      animated: i === active,
      style: {
        stroke: COLORS[i % COLORS.length],
        strokeWidth: i === active ? 4 : 2.5,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: COLORS[i % COLORS.length],
      },
    }),
  );
  edges.push({
    id: "fault-edge",
    source: states[Math.min(2, states.length - 1)],
    target: "fault",
    label: "timeout / interlock",
    style: { stroke: "#c9473c", strokeWidth: 2.5, strokeDasharray: "6 4" },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#c9473c" },
  });
  return (
    <div className="fsm-graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
      >
        <Background color="#dce5e1" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
      <div className="fsm-legend">
        <span>
          <i className="current" />
          Current
        </span>
        <span>
          <i />
          Reachable state
        </span>
        <span>
          <i className="fault" />
          Fault transition
        </span>
      </div>
    </div>
  );
}

export function BehaviourGraph({
  kind,
  tick,
}: {
  kind: "F" | "G";
  tick: number;
}) {
  const f = kind === "F";
  const labels = f
    ? ["IDLE", "ACQUIRE", "TRANSPORT", "EXECUTE", "VERIFY"]
    : ["INPUT", "STORE", "PROCESS", "SORT", "OUTPUT", "REWORK"];
  const positions = f
    ? [
        { x: 30, y: 100 },
        { x: 260, y: 10 },
        { x: 500, y: 100 },
        { x: 380, y: 240 },
        { x: 120, y: 240 },
      ]
    : [
        { x: 10, y: 90 },
        { x: 210, y: 90 },
        { x: 410, y: 90 },
        { x: 610, y: 90 },
        { x: 810, y: 90 },
        { x: 410, y: 260 },
      ];
  const active = tick % (f ? 5 : 5);
  const nodes: Node[] = labels.map((x, i) => ({
    id: x,
    position: positions[i],
    data: { label: ellipse(x, i, i === active) },
    style: { width: 145, border: 0, background: "transparent", padding: 0 },
  }));
  const pairs = f
    ? [
        ["IDLE", "ACQUIRE", "workpiece"],
        ["ACQUIRE", "TRANSPORT", "grip confirmed"],
        ["TRANSPORT", "EXECUTE", "station ready"],
        ["EXECUTE", "VERIFY", "cycle done"],
        ["VERIFY", "IDLE", "accepted"],
      ]
    : [
        ["INPUT", "STORE", "identified"],
        ["STORE", "PROCESS", "order released"],
        ["PROCESS", "SORT", "process complete"],
        ["SORT", "OUTPUT", "quality pass"],
        ["SORT", "REWORK", "quality fail"],
        ["REWORK", "PROCESS", "retry < 2"],
      ];
  const edges: Edge[] = pairs.map((x, i) => ({
    id: `b${i}`,
    source: x[0],
    target: x[1],
    label: x[2],
    type: "smoothstep",
    animated: i === active,
    style: {
      stroke: COLORS[i % COLORS.length],
      strokeWidth: i === active ? 4 : 2.5,
      strokeDasharray: i > 3 && !f ? "6 4" : undefined,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: COLORS[i % COLORS.length],
    },
  }));
  return (
    <div className={`behaviour-graph ${f ? "f-model" : "g-model"}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
      >
        <Background color="#e0e8e4" gap={18} />
      </ReactFlow>
    </div>
  );
}

export function FSMCatalogue({
  tick,
  onSelect,
}: {
  tick: number;
  onSelect: (id: string) => void;
}) {
  return (
    <section className="fsm-catalogue">
      <header>
        <b>Station FSM catalogue</b>
        <span>All executable station models · select one to inspect</span>
      </header>
      <div>
        {Object.entries(stationStates).map(([id, states]) => (
          <button key={id} onClick={() => onSelect(id)}>
            <strong>{id}</strong>
            <span>
              {states.map((s, i) => (
                <i
                  className={i === tick % states.length ? "active" : ""}
                  key={s}
                >
                  {s}
                </i>
              ))}
            </span>
            <em>{states.length} states</em>
          </button>
        ))}
      </div>
    </section>
  );
}
