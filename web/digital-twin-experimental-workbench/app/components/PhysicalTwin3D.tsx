"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Grid, Html, OrbitControls } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

export type TwinStation = {
  id: string;
  name: string;
  state: string;
  active: boolean;
};

const STEEL = "#aeb7b8",
  DARK = "#151919",
  RED = "#e12e2b",
  BLUE = "#1976d2",
  GREEN = "#16a085";
const stationPositions: Record<string, [number, number, number]> = {
  DSI: [1.2, 0, -3.15],
  VGR: [4.4, 0, 0.8],
  HBW: [0.2, 0, 0.9],
  MPO: [-4.1, 0, 1.35],
  SLD: [-4.25, 0, -2],
  DSO: [2.5, 0, -3.15],
};
const route = [
  stationPositions.DSI,
  [2.6, 0.75, -1.5],
  stationPositions.HBW,
  [-2, 0.75, 0.9],
  stationPositions.MPO,
  [-4.1, 0.75, -0.5],
  stationPositions.SLD,
  stationPositions.DSO,
];

function Beam({
  p,
  s,
  c = DARK,
}: {
  p: [number, number, number];
  s: [number, number, number];
  c?: string;
}) {
  return (
    <mesh position={p} castShadow receiveShadow>
      <boxGeometry args={s} />
      <meshStandardMaterial color={c} metalness={0.35} roughness={0.55} />
    </mesh>
  );
}
function Label({
  id,
  name,
  active,
}: {
  id: string;
  name: string;
  active: boolean;
}) {
  return (
    <Html position={[0, 3.05, 0]} center distanceFactor={10}>
      <div className={`scene-label ${active ? "active" : ""}`}>
        <b>{id}</b>
        <span>{name}</span>
      </div>
    </Html>
  );
}
function Frame({
  width = 3,
  depth = 2.4,
  height = 2.5,
}: {
  width?: number;
  depth?: number;
  height?: number;
}) {
  const posts = [
    [-width / 2, height / 2, -depth / 2],
    [width / 2, height / 2, -depth / 2],
    [-width / 2, height / 2, depth / 2],
    [width / 2, height / 2, depth / 2],
  ] as [number, number, number][];
  return (
    <group>
      {posts.map((p, i) => (
        <group key={i}>
          <Beam p={p} s={[0.16, height, 0.16]} />
          {[0.35, 0.8, 1.25, 1.7, 2.15, 2.6, 3.05]
            .filter((y) => y < height)
            .map((y) => (
              <Beam
                key={y}
                p={[p[0], y, p[2]]}
                s={[0.25, 0.08, 0.25]}
                c={RED}
              />
            ))}
        </group>
      ))}
      <Beam p={[0, 0.12, 0]} s={[width, 0.18, depth]} />
      <Beam p={[0, height, 0]} s={[width, 0.14, depth]} c={RED} />
    </group>
  );
}
function Conveyor({
  length = 2.8,
  active = false,
}: {
  length?: number;
  active?: boolean;
}) {
  const rollers = Array.from(
    { length: 8 },
    (_, i) => -length / 2 + 0.2 + (i * (length - 0.4)) / 7,
  );
  return (
    <group>
      {rollers.map((x, i) => (
        <mesh
          key={i}
          position={[x, 0.55, 0]}
          rotation={[Math.PI / 2, 0, 0]}
          castShadow
        >
          <cylinderGeometry args={[0.12, 0.12, 1.05, 16]} />
          <meshStandardMaterial
            color={active && i % 2 === 0 ? GREEN : STEEL}
            metalness={0.7}
          />
        </mesh>
      ))}
      <Beam p={[0, 0.4, 0.6]} s={[length, 0.14, 0.12]} />
      <Beam p={[0, 0.4, -0.6]} s={[length, 0.14, 0.12]} />
    </group>
  );
}
function DSI({ station }: { station: TwinStation }) {
  return (
    <group position={stationPositions.DSI}>
      <Frame width={2.3} depth={1.5} height={1.45} />
      <Conveyor length={2.1} active={station.active} />
      <mesh position={[-0.65, 0.85, 0]}>
        <boxGeometry args={[0.35, 0.45, 1.2]} />
        <meshStandardMaterial color={RED} />
      </mesh>
      <mesh position={[0.62, 0.92, -0.55]}>
        <boxGeometry args={[0.18, 0.7, 0.18]} />
        <meshStandardMaterial color="#f3d629" />
      </mesh>
      <Label id="DPS-IN" name="Delivery + NFC" active={station.active} />
    </group>
  );
}
function HBW({ station, t }: { station: TwinStation; t: number }) {
  const lift = station.active ? 0.65 + Math.sin(t * 2) * 0.45 : 0.65;
  return (
    <group position={stationPositions.HBW}>
      <Frame width={3.8} depth={2.2} height={3.8} />
      {[-1.2, 0, 1.2].map((x) =>
        [0.75, 1.75, 2.75].map((y, j) => (
          <group key={`${x}${j}`}>
            <Beam p={[x, y, 0]} s={[0.95, 0.12, 1.65]} c="#252929" />
            <mesh position={[x, y + 0.22, 0]}>
              <cylinderGeometry args={[0.23, 0.23, 0.27, 24]} />
              <meshStandardMaterial
                color={
                  (x + j) % 3 === 0 ? BLUE : (x + j) % 3 === 1 ? "#f1f2f1" : RED
                }
              />
            </mesh>
          </group>
        )),
      )}
      <group position={[0, 1 + lift, -1.25]}>
        <Beam p={[0, 0, 0]} s={[1, 0.12, 0.65]} c={RED} />
        <Beam p={[0, -1, 0]} s={[0.12, 2, 0.12]} c={STEEL} />
      </group>
      <Label id="HBW" name="9-bin high-bay warehouse" active={station.active} />
    </group>
  );
}
function VGR({ station, t }: { station: TwinStation; t: number }) {
  const x = station.active ? Math.sin(t * 0.8) * 0.75 : 0;
  const y = station.active ? 2.1 + Math.sin(t * 1.6) * 0.35 : 2.1;
  return (
    <group position={stationPositions.VGR}>
      <Frame width={2.5} depth={2.2} height={3.7} />
      <Beam p={[x, 3.42, 0]} s={[0.45, 0.35, 1.8]} c={RED} />
      <Beam p={[x, y, 0]} s={[0.18, 2.15, 0.18]} c={STEEL} />
      <Beam p={[x + 0.25, y + 0.15, 0]} s={[0.28, 0.38, 0.8]} c={RED} />
      <mesh position={[x, y - 0.98, 0]}>
        <cylinderGeometry args={[0.22, 0.34, 0.22, 24]} />
        <meshStandardMaterial color={DARK} />
      </mesh>
      <Label id="VGR" name="3-axis vacuum gripper" active={station.active} />
    </group>
  );
}
function MPO({ station, t }: { station: TwinStation; t: number }) {
  return (
    <group position={stationPositions.MPO}>
      <Frame width={3.2} depth={2.5} height={2.1} />
      <mesh
        position={[0, 0.7, 0]}
        rotation={[0, station.active ? t * 1.7 : 0, 0]}
      >
        <cylinderGeometry args={[0.92, 0.92, 0.15, 32]} />
        <meshStandardMaterial color={BLUE} metalness={0.45} />
      </mesh>
      <mesh position={[0.7, 1.4, 0.25]}>
        <boxGeometry args={[0.9, 1.4, 1.3]} />
        <meshStandardMaterial color="#d8dee0" />
      </mesh>
      <mesh position={[0.7, 1.45, -0.43]}>
        <boxGeometry args={[0.58, 0.74, 0.05]} />
        <meshStandardMaterial
          color={station.active ? "#ff9e3d" : "#494f50"}
          emissive={station.active ? "#ff6b00" : "#000"}
          emissiveIntensity={0.8}
        />
      </mesh>
      <Label id="MPO" name="Machining + kiln" active={station.active} />
    </group>
  );
}
function SLD({ station, t }: { station: TwinStation; t: number }) {
  return (
    <group position={stationPositions.SLD}>
      <Frame width={3.3} depth={2.2} height={1.65} />
      <Conveyor length={3.1} active={station.active} />
      <Beam p={[0.5, 0.85, 0]} s={[0.12, 0.85, 0.12]} c={BLUE} />
      <group
        position={[0.7, 0.68, 0]}
        rotation={[0, station.active ? Math.sin(t * 3) * 0.6 : 0, 0]}
      >
        <Beam p={[0, 0, 0]} s={[1.2, 0.12, 0.12]} c={RED} />
      </group>
      <Label id="SLD" name="Sorting + colour sensor" active={station.active} />
    </group>
  );
}
function DSO({ station }: { station: TwinStation }) {
  return (
    <group position={stationPositions.DSO}>
      <Frame width={1.7} depth={1.5} height={1.45} />
      <Conveyor length={1.5} active={station.active} />
      <mesh position={[0.5, 0.42, 0.75]} rotation={[0, 0, -0.18]}>
        <boxGeometry args={[0.8, 0.1, 1.1]} />
        <meshStandardMaterial color={RED} />
      </mesh>
      <Label
        id="DPS-OUT"
        name="Pickup + quality control"
        active={station.active}
      />
    </group>
  );
}
function Infrastructure() {
  return (
    <group>
      <Beam p={[0, -0.08, 0]} s={[12.8, 0.16, 8.1]} c="#d9dcda" />
      <group position={[5.1, 0, -2.25]}>
        <Beam p={[0, 0.18, 0]} s={[3.1, 0.36, 2.2]} c="#181b1b" />
        {[-1.05, -0.52, 0, 0.52, 1.05].map((x, i) => (
          <mesh key={i} position={[x, 0.85, 0]} castShadow>
            <boxGeometry args={[0.43, 1.15, 1.45]} />
            <meshStandardMaterial
              color={i === 0 ? "#8b9698" : "#b4bec0"}
              metalness={0.25}
            />
            {i > 0 && (
              <mesh position={[0, 0.15, 0.73]}>
                <boxGeometry args={[0.18, 0.25, 0.04]} />
                <meshStandardMaterial
                  color={GREEN}
                  emissive={GREEN}
                  emissiveIntensity={0.4}
                />
              </mesh>
            )}
          </mesh>
        ))}
        <Html position={[0, 1.7, 0]} center distanceFactor={10}>
          <div className="scene-label">
            <b>S7-1500</b>
            <span>PLC + 24V connection board</span>
          </div>
        </Html>
      </group>
      <group position={[-0.7, 0.2, -3.25]}>
        <mesh castShadow>
          <boxGeometry args={[1.05, 0.45, 0.72]} />
          <meshStandardMaterial color="#252a2b" />
        </mesh>
        <mesh position={[0, 0.08, 0.37]}>
          <boxGeometry args={[0.18, 0.12, 0.03]} />
          <meshStandardMaterial color={GREEN} emissive={GREEN} />
        </mesh>
        <Html position={[0, 0.75, 0]} center distanceFactor={10}>
          <div className="scene-label">
            <b>IoT</b>
            <span>Raspberry Pi + Node-RED</span>
          </div>
        </Html>
      </group>
      <group position={[-2.05, 0, -3.1]}>
        <Beam p={[0, 0.85, 0]} s={[0.14, 1.6, 0.14]} c={RED} />
        <mesh position={[0, 1.62, 0]} rotation={[0, 0, 0.25]}>
          <boxGeometry args={[0.48, 0.3, 0.3]} />
          <meshStandardMaterial color={DARK} />
        </mesh>
        <mesh position={[0.12, 1.62, 0.05]}>
          <sphereGeometry args={[0.08, 12, 12]} />
          <meshStandardMaterial
            color="#4a94ff"
            emissive="#4a94ff"
            emissiveIntensity={0.8}
          />
        </mesh>
        <Html position={[0, 2.1, 0]} center distanceFactor={10}>
          <div className="scene-label">
            <b>SSC</b>
            <span>Camera + environment sensor</span>
          </div>
        </Html>
      </group>
    </group>
  );
}
function Workpiece({ t, color }: { t: number; color: string }) {
  const ref = useRef<THREE.Group>(null);
  useFrame(() => {
    if (!ref.current) return;
    const p = (t * 0.055) % route.length,
      a = route[Math.floor(p)],
      b = route[(Math.floor(p) + 1) % route.length],
      f = p % 1;
    ref.current.position.set(
      THREE.MathUtils.lerp(a[0], b[0], f),
      0.92 + Math.sin(f * Math.PI) * 0.35,
      THREE.MathUtils.lerp(a[2], b[2], f),
    );
    ref.current.rotation.y += 0.025;
  });
  return (
    <group ref={ref}>
      <mesh castShadow>
        <cylinderGeometry args={[0.28, 0.28, 0.22, 32]} />
        <meshStandardMaterial color={color} metalness={0.15} roughness={0.35} />
      </mesh>
      <pointLight color={color} intensity={1.4} distance={2.2} />
    </group>
  );
}
function Scene({
  stations,
  t,
  color,
  autoRotate,
}: {
  stations: TwinStation[];
  t: number;
  color: string;
  autoRotate: boolean;
}) {
  const by = (id: string) => stations.find((s) => s.id === id)!;
  return (
    <>
      <color attach="background" args={["#edf1ef"]} />
      <fog attach="fog" args={["#edf1ef", 18, 30]} />
      <ambientLight intensity={1.6} />
      <directionalLight
        castShadow
        position={[7, 12, -5]}
        intensity={2.2}
        shadow-mapSize={[1024, 1024]}
      />
      <Environment preset="warehouse" />
      <group position={[0, 0, 0]}>
        <Infrastructure />
        <DSI station={by("DSI")} />
        <VGR station={by("VGR")} t={t} />
        <HBW station={by("HBW")} t={t} />
        <MPO station={by("MPO")} t={t} />
        <SLD station={by("SLD")} t={t} />
        <DSO station={by("DSO")} />
        <Workpiece t={t} color={color} />
      </group>
      <Grid
        position={[0, -0.18, 0]}
        args={[20, 16]}
        cellSize={0.5}
        cellThickness={0.25}
        cellColor="#aab4b1"
        sectionSize={2}
        sectionThickness={0.8}
        sectionColor="#6e807b"
        fadeDistance={24}
      />
      <OrbitControls
        makeDefault
        enableDamping
        minDistance={8}
        maxDistance={25}
        maxPolarAngle={Math.PI / 2.02}
        target={[0, 1, 0]}
        autoRotate={autoRotate}
        autoRotateSpeed={0.45}
      />
    </>
  );
}

export default function PhysicalTwin3D({
  stations,
  tick,
  running,
  speed,
  color,
  autoRotate,
}: {
  stations: TwinStation[];
  tick: number;
  running: boolean;
  speed: number;
  color: string;
  autoRotate: boolean;
}) {
  const t = useMemo(() => tick * speed, [tick, speed]);
  return (
    <div className="twin-canvas">
      <Canvas
        shadows
        dpr={[1, 1.5]}
        camera={{ position: [11, 9, 14], fov: 40, near: 0.1, far: 80 }}
        gl={{ antialias: true, powerPreference: "high-performance" }}
      >
        <Scene
          stations={stations}
          t={t}
          color={color}
          autoRotate={autoRotate}
        />
      </Canvas>
      {!running && <div className="scene-paused">PAUSED</div>}
      <div className="scene-help">
        Fischertechnik 560840 reconstruction · Drag to orbit · Scroll to zoom
      </div>
    </div>
  );
}
