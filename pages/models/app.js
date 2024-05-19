import { IFCLoader } from "./components/IFCLoader.js";
import {
  AmbientLight,
  AxesHelper,
  DirectionalLight,
  GridHelper,
  PerspectiveCamera,
  Scene,
  Raycaster,
  Vector2,
  WebGLRenderer,
  MeshBasicMaterial,
} from "./components/three.module.js";
import { OrbitControls } from "./components/OrbitControls.js";
import {
  acceleratedRaycast,
  computeBoundsTree,
  disposeBoundsTree
} from './components/three-mesh-bvh/three-mesh-bvh.js';
import { OBJLoader } from './components/OBJLoader.js'; // Импорт OBJLoader

// Инициализация переменных и констант
const ifcModels = [];
const ifcLoader = new IFCLoader();
const size = { width: window.innerWidth, height: window.innerHeight };
const materialParams = {
  transparent: true,
  opacity: 0.6,
  depthTest: false
};
const preselectMat = new MeshBasicMaterial({ ...materialParams, color: 0xf1a832 });
const selectMat = new MeshBasicMaterial({ ...materialParams, color: 0xc63f35 });
const sendValue = value => Streamlit.setComponentValue(value);
const scene = new Scene();

const setup = () => {
  const ifc = ifcLoader.ifcManager;
  const camera = new PerspectiveCamera(75, size.width / size.height);
  camera.position.set(8, 13, 15);
  camera.far = 10000; // Установка неограниченной дальности обзора камеры

  // Настройка освещения
  const lightColor = 0xffffff;
  const ambientLight = new AmbientLight(lightColor, 0.5);
  const directionalLight = new DirectionalLight(lightColor, 1);
  directionalLight.position.set(0, 10, 0);
  directionalLight.target.position.set(-5, 0, 0);
  scene.add(ambientLight, directionalLight, directionalLight.target);

  // Настройка рендерера
  const renderer = new WebGLRenderer({ canvas: document.getElementById("three-canvas"), alpha: true, antialias: true });
  renderer.setSize(size.width, size.height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Добавление вспомогательных объектов
  const grid = new GridHelper(50, 30);
  const axes = new AxesHelper();
  axes.material.depthTest = false;
  axes.renderOrder = 1;
  scene.add(grid, axes);

  // Настройка управления камерой
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(-2, 0, 0);

  // Анимация сцены
  const animate = () => {
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  };
  animate();

  // Адаптация размеров экрана
  const adjustViewport = () => {
    size.width = window.innerWidth;
    size.height = window.innerHeight;
    camera.aspect = size.width / size.height;
    camera.updateProjectionMatrix();
    renderer.setSize(size.width, size.height);
  };
  window.addEventListener("resize", adjustViewport);

  // Настройка IFC
  ifc.setWasmPath("./components/IFC/");
  ifc.setupThreeMeshBVH(computeBoundsTree, disposeBoundsTree, acceleratedRaycast);

  // Настройка Raycaster
  const raycaster = new Raycaster();
  raycaster.firstHitOnly = true;
  const mouse = new Vector2();

  // Функция получения пересечения объектов
  const getIntersection = (event) => {
    const bounds = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - bounds.left) / (bounds.right - bounds.left)) * 2 - 1;
    mouse.y = -((event.clientY - bounds.top) / (bounds.bottom - bounds.top)) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const found = raycaster.intersectObjects(ifcModels);
    if (found[0]) return { "id": ifc.getExpressId(found[0].object.geometry, found[0].faceIndex), "modelID": found[0].object.modelID };
  };

  // Функция получения данных объекта
  const getObjectData = (event) => {
    const intersection = getIntersection(event);
    if (intersection) {
      const objectId = intersection.id;
      return JSON.stringify({ "id": objectId }, null, 2);
    }
  };


  const highlightModel = { id: -1 };
  const selectModel = { id: -1 };

  // Функция выделения модели
  const highlight = (event, material, model) => {
    const intersection = getIntersection(event);
    if (intersection) ifc.createSubset({ modelID: intersection.modelID, ids: [intersection.id], material: material, scene: scene, removePrevious: true });
    else ifc.removeSubset(model.id, scene, material);
  };

  // Обработчики событий
  window.onmousemove = (event) => highlight(event, preselectMat, highlightModel);
  window.ondblclick = (event) => {
    highlight(event, selectMat, selectModel);
    sendValue(getObjectData(event));
  };

  // Загрузка и добавление OBJ модели города
  const objLoader = new OBJLoader();
  objLoader.load(
    './city.obj', // Путь к модели города в формате OBJ
    (object) => {
      scene.add(object);
      // Настройка позиции и масштаба модели города
      object.position.set(0, 0, 0); // Настройте позицию по вашему усмотрению
      object.scale.set(10, 10, 10); // Масштабируем размер модели по вашему усмотрению
    },
    undefined,
    (error) => {
      console.error('Ошибка загрузки модели:', error);
    }
  );
};

// Функция загрузки IFC модели
const sigmaLoader = async (url) => {
  const ifcModel = await ifcLoader.ifcManager.parse(url);
  ifcModels.push(ifcModel.mesh);
  scene.add(ifcModel.mesh);
};

// Функция обработки события загрузки URL
const loadURL = async (event) => {
  if (!window.rendered) {
    const { url } = event.detail.args;
    await sigmaLoader(url);
    window.rendered = true;
  }
};

// Инициализация Streamlit компонента
Streamlit.loadViewer(setup);
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, loadURL);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(window.innerWidth / 1.4);
