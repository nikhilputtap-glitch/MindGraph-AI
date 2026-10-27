import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

gsap.registerPlugin(ScrollTrigger);

const canvas = document.getElementById("world");
const loader = document.getElementById("loader");

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x05070b, 0.045);

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 200);
camera.position.set(0, 1.4, 14);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0x05070b, 1);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.85, 0.7, 0.18);
composer.addPass(bloom);

scene.add(new THREE.AmbientLight(0x1a2233, 0.7));
const key = new THREE.PointLight(0xd4b483, 28, 40);
key.position.set(6, 8, 8);
scene.add(key);
const rim = new THREE.PointLight(0x7ec8d8, 18, 50);
rim.position.set(-8, -2, 4);
scene.add(rim);

function makeStarTexture() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(0.35, "rgba(240,215,168,0.7)");
  g.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const starCount = 2800;
const starGeo = new THREE.BufferGeometry();
const starPos = new Float32Array(starCount * 3);
const starCol = new Float32Array(starCount * 3);
for (let i = 0; i < starCount; i++) {
  const r = 18 + Math.random() * 55;
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(2 * Math.random() - 1);
  starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
  starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.55;
  starPos[i * 3 + 2] = r * Math.cos(phi);
  const gold = Math.random() > 0.72;
  starCol[i * 3] = gold ? 0.92 : 0.72;
  starCol[i * 3 + 1] = gold ? 0.78 : 0.86;
  starCol[i * 3 + 2] = gold ? 0.52 : 0.95;
}
starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
starGeo.setAttribute("color", new THREE.BufferAttribute(starCol, 3));
const stars = new THREE.Points(
  starGeo,
  new THREE.PointsMaterial({
    size: 0.085,
    map: makeStarTexture(),
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexColors: true,
  })
);
scene.add(stars);

const coreGeo = new THREE.IcosahedronGeometry(1.65, 2);
const coreMat = new THREE.MeshStandardMaterial({
  color: 0x0b1220,
  metalness: 0.85,
  roughness: 0.25,
  emissive: 0x142033,
  emissiveIntensity: 0.6,
});
const core = new THREE.Mesh(coreGeo, coreMat);
scene.add(core);

const wire = new THREE.Mesh(
  new THREE.IcosahedronGeometry(1.72, 1),
  new THREE.MeshBasicMaterial({
    color: 0xd4b483,
    wireframe: true,
    transparent: true,
    opacity: 0.35,
  })
);
scene.add(wire);

const innerGlow = new THREE.Mesh(
  new THREE.SphereGeometry(1.15, 32, 32),
  new THREE.MeshBasicMaterial({
    color: 0x7ec8d8,
    transparent: true,
    opacity: 0.18,
  })
);
scene.add(innerGlow);

function ring(radius, color, tilt) {
  const geo = new THREE.TorusGeometry(radius, 0.012, 16, 180);
  const mat = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0.55,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.rotation.x = tilt;
  scene.add(mesh);
  return mesh;
}

const rings = [
  ring(3.2, 0xd4b483, Math.PI / 2.4),
  ring(4.4, 0x7ec8d8, Math.PI / 3.1),
  ring(5.8, 0x9aa3b2, Math.PI / 5),
];

const nodeGroup = new THREE.Group();
scene.add(nodeGroup);
const nodeGeo = new THREE.OctahedronGeometry(0.12, 0);
const accents = [0xd4b483, 0x7ec8d8, 0xf0d7a8];
for (let i = 0; i < 18; i++) {
  const m = new THREE.Mesh(
    nodeGeo,
    new THREE.MeshStandardMaterial({
      color: accents[i % 3],
      emissive: accents[i % 3],
      emissiveIntensity: 1.4,
      metalness: 0.6,
      roughness: 0.2,
    })
  );
  const a = (i / 18) * Math.PI * 2;
  const r = 3.2 + (i % 3) * 1.1;
  m.position.set(Math.cos(a) * r, Math.sin(a * 1.7) * 0.8, Math.sin(a) * r);
  m.userData.base = m.position.clone();
  m.userData.speed = 0.4 + (i % 5) * 0.12;
  nodeGroup.add(m);
}

const camTarget = { x: 0, y: 1.4, z: 14, lookY: 0, rotY: 0 };
const mouse = { x: 0, y: 0 };

window.addEventListener("pointermove", (e) => {
  mouse.x = (e.clientX / innerWidth - 0.5) * 2;
  mouse.y = (e.clientY / innerHeight - 0.5) * 2;
});

ScrollTrigger.create({
  trigger: document.body,
  start: "top top",
  end: "bottom bottom",
  scrub: 1.1,
  onUpdate: (self) => {
    const t = self.progress;
    camTarget.x = Math.sin(t * Math.PI * 1.4) * 4.2;
    camTarget.y = 1.2 + Math.cos(t * Math.PI * 2) * 1.6;
    camTarget.z = 14 - t * 8.5;
    camTarget.lookY = Math.sin(t * Math.PI) * 0.6;
    camTarget.rotY = t * 0.9;
    bloom.strength = 0.7 + t * 0.45;
  },
});

gsap.from(".hud", { y: -30, opacity: 0, duration: 1.4, delay: 2.1, ease: "power3.out" });
gsap.from("#hero > *", {
  y: 40,
  opacity: 0,
  stagger: 0.12,
  duration: 1.2,
  delay: 2.15,
  ease: "power3.out",
});

document.querySelectorAll(".panel").forEach((panel) => {
  gsap.from(panel.children, {
    scrollTrigger: { trigger: panel, start: "top 78%" },
    y: 36,
    opacity: 0,
    duration: 1,
    stagger: 0.08,
    ease: "power3.out",
  });
});

window.addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight);
  bloom.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();

function tick() {
  const t = clock.getElapsedTime();
  core.rotation.y = t * 0.18;
  core.rotation.x = t * 0.07;
  wire.rotation.y = -t * 0.12;
  wire.rotation.z = t * 0.05;
  innerGlow.scale.setScalar(1 + Math.sin(t * 1.6) * 0.06);
  stars.rotation.y = t * 0.012;
  rings[0].rotation.z = t * 0.22;
  rings[1].rotation.z = -t * 0.16;
  rings[2].rotation.y = t * 0.1;
  nodeGroup.children.forEach((n, i) => {
    const b = n.userData.base;
    n.position.y = b.y + Math.sin(t * n.userData.speed + i) * 0.25;
    n.rotation.y = t * 0.8;
  });

  camera.position.x += (camTarget.x + mouse.x * 0.9 - camera.position.x) * 0.045;
  camera.position.y += (camTarget.y - mouse.y * 0.55 - camera.position.y) * 0.045;
  camera.position.z += (camTarget.z - camera.position.z) * 0.045;
  camera.lookAt(Math.sin(t * 0.1) * 0.3 + mouse.x * 0.25, camTarget.lookY, 0);

  composer.render();
  requestAnimationFrame(tick);
}

window.addEventListener("load", () => {
  setTimeout(() => loader.classList.add("done"), 1900);
  tick();
});
