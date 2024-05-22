import { IFCLoader } from "./components/IFCLoader.js";
import { AmbientLight, AxesHelper, DirectionalLight, GridHelper, PerspectiveCamera, Scene, Raycaster, Vector2, WebGLRenderer, MeshBasicMaterial, Plane, PlaneHelper, Vector3, DoubleSide, Mesh, PlaneGeometry } from "./components/three.module.js";
import { OrbitControls } from "./components/OrbitControls.js";
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from './components/three-mesh-bvh/three-mesh-bvh.js';

const ifcModels = [];
const ifcLoader = new IFCLoader();
const size = { width: window.innerWidth, height: window.innerHeight };
const materialParams = { transparent: true, opacity: 0.6, depthTest: false };
const preselectMat = new MeshBasicMaterial({ ...materialParams, color: 0xf1a832 });
const selectMat = new MeshBasicMaterial({ ...materialParams, color: 0xc63f35 });
const sendValue = value => Streamlit.setComponentValue(value);
const scene = new Scene();

let clippingEnabled = false;
const gap = 0.01; // Зазор между плоскостями

const plane = new Plane(new Vector3(0, -1, 0), gap);
const planeHelper = new PlaneHelper(plane, 10);
planeHelper.visible = false; // Hide clipping plane by default

let verticalClippingEnabled = false;
const verticalPlane = new Plane(new Vector3(1, 0, 0), gap);
const verticalPlaneHelper = new PlaneHelper(verticalPlane, 10);
verticalPlaneHelper.visible = false; // Hide vertical clipping plane by default

const largePlaneSize = 100; // Определение размера для сеток

// Create grid helpers for clipping planes
const horizontalGrid = new GridHelper(largePlaneSize, 100, 0xff0000, 0xff0000);
horizontalGrid.rotation.x = Math.PI;
horizontalGrid.visible = false;

const verticalGrid = new GridHelper(largePlaneSize, 100, 0x00ff00, 0x00ff00);
verticalGrid.rotation.z = Math.PI / 2;
verticalGrid.visible = false;

scene.add(horizontalGrid);
scene.add(verticalGrid);

const setup = () => {
  const ifc = ifcLoader.ifcManager;
  const camera = new PerspectiveCamera(75, size.width / size.height);
  camera.position.set(8, 13, 15);
  camera.far = 10000;

  const lightColor = 0xffffff;
  const ambientLight = new AmbientLight(lightColor, 0.5);
  const directionalLight = new DirectionalLight(lightColor, 1);
  directionalLight.position.set(0, 10, 0);
  directionalLight.target.position.set(-5, 0, 0);
  scene.add(ambientLight, directionalLight, directionalLight.target);

  const renderer = new WebGLRenderer({ canvas: document.getElementById("three-canvas"), alpha: true, antialias: true });
  renderer.setSize(size.width, size.height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const grid = new GridHelper(50, 30);
  const axes = new AxesHelper();
  axes.material.depthTest = false;
  axes.renderOrder = 1;
  scene.add(grid, axes);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(-2, 0, 0);

  const animate = () => {
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  };
  animate();

  const adjustViewport = () => {
    size.width = window.innerWidth;
    size.height = window.innerHeight;
    camera.aspect = size.width / size.height;
    camera.updateProjectionMatrix();
    renderer.setSize(size.width, size.height);
  };
  window.addEventListener("resize", adjustViewport);

  ifc.setWasmPath("./components/IFC/");
  ifc.setupThreeMeshBVH(computeBoundsTree, disposeBoundsTree, acceleratedRaycast);

  const raycaster = new Raycaster();
  raycaster.firstHitOnly = true;
  const mouse = new Vector2();

  const getIntersection = (event) => {
    const bounds = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - bounds.left) / (bounds.right - bounds.left)) * 2 - 1;
    mouse.y = -((event.clientY - bounds.top) / (bounds.bottom - bounds.top)) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const found = raycaster.intersectObjects(ifcModels);
    if (found[0]) return { "id": ifc.getExpressId(found[0].object.geometry, found[0].faceIndex), "modelID": found[0].object.modelID };
  };

  const getObjectData = (event) => {
    const intersection = getIntersection(event);
    if (intersection) {
      const objectId = intersection.id;
      return JSON.stringify({ "id": objectId }, null, 2);
    }
  };

  const highlightModel = { id: -1 };
  const selectModel = { id: -1 };

  const highlight = (event, material, model) => {
    const intersection = getIntersection(event);
    if (intersection) ifc.createSubset({ modelID: intersection.modelID, ids: [intersection.id], material: material, scene: scene, removePrevious: true });
    else ifc.removeSubset(model.id, scene, material);
  };

  window.onmousemove = (event) => highlight(event, preselectMat, highlightModel);
  window.ondblclick = (event) => {
    highlight(event, selectMat, selectModel);
    sendValue(getObjectData(event));
  };

  const updateClippingPlanes = () => {
    renderer.clippingPlanes = [
      ...(clippingEnabled ? [plane] : []),
      ...(verticalClippingEnabled ? [verticalPlane] : [])
    ];

    // Update horizontal clipping grid
    horizontalGrid.visible = clippingEnabled;
    if (clippingEnabled) {
      horizontalGrid.position.copy(plane.normal).multiplyScalar(-plane.constant + gap); // -plane.constant исправляет, но появляеться мерцание
    }


    // Update vertical clipping grid
    verticalGrid.visible = verticalClippingEnabled;
    if (verticalClippingEnabled) {
      verticalGrid.position.copy(verticalPlane.normal).multiplyScalar(-verticalPlane.constant + gap); // -verticalPlane.constant исправляет, но появляеться мерцание
    }

  };

  const step = 0.3; // скорость изменения движения секущей плоскости (по хорошему нужно вывести это через Streamlit сбоку)

  window.addEventListener('keydown', (event) => {
    if (event.key === '-' || event.key === '=') {
      if (clippingEnabled) {
        if (event.key === '-') plane.constant -= step;
        else if (event.key === '=') plane.constant += step;
        updateClippingPlanes();
        
      }
    } else if (event.key === '2') {
      clippingEnabled = !clippingEnabled;
      planeHelper.visible = clippingEnabled;
      updateClippingPlanes();
      if (!verticalClippingEnabled) {
        grid.visible = !clippingEnabled;
      }
    }
  });

  window.addEventListener('keydown', (event) => {
    if (event.key === '9' || event.key === '0') {
      if (verticalClippingEnabled) {
        if (event.key === '9') verticalPlane.constant -= step;
        else if (event.key === '0') verticalPlane.constant += step;
        updateClippingPlanes();
      }
    } else if (event.key === '1') {
      verticalClippingEnabled = !verticalClippingEnabled;
      verticalPlaneHelper.visible = verticalClippingEnabled;
      updateClippingPlanes();
      if (!clippingEnabled) {
        grid.visible = !verticalClippingEnabled;
      }
    }
  });
};

const sigmaLoader = async (url) => {
  const ifcModel = await ifcLoader.ifcManager.parse(url);
  ifcModels.push(ifcModel.mesh);
  scene.add(ifcModel.mesh);
};

const loadURL = async (event) => {
  if (!window.rendered) {
    const { url } = event.detail.args;
    await sigmaLoader(url);
    window.rendered = true;
  }
};

Streamlit.loadViewer(setup);
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, loadURL);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(window.innerWidth / 1.4);
