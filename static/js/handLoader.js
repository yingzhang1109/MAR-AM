if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var camera, scene, renderer;
const manager = new THREE.LoadingManager();
init();
  
function init() {
  scene = new THREE.Scene()
  scene.add( new THREE.AmbientLight( 0x999999) );
  
  
  camera = new THREE.PerspectiveCamera( 70, 0.75*window.innerWidth / window.innerHeight, 0.1, 500000);

  // Z is up for objects intended to be 3D printed.

  //camera.up.set( 0, 0, 20 );
  camera.position.set( 0, 0, 20 );

  camera.add( new THREE.PointLight( 0xffffff, 0.8 ) );

  scene.add( camera );

  var grid = new THREE.GridHelper( 25, 50, 0xffffff, 0x555555 );
  grid.rotateOnAxis( new THREE.Vector3( 1, 0, 0 ), 90 * ( Math.PI/180 ) );
  scene.add( grid );

  renderer = new THREE.WebGLRenderer( { canvas: document.querySelector('#canvas1') });
  renderer.setClearColor( 0x999999 );
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( 0.6*window.innerWidth, 0.8*window.innerHeight, false );
  document.body.appendChild( renderer.domElement );
  

  
  var controls = new THREE.OrbitControls( camera, renderer.domElement );
  controls.addEventListener( 'change', render );
  controls.target.set( 0, 1.2, 2 );
  controls.update();
  window.addEventListener( 'resize', onWindowResize, false );

}

function onWindowResize() {

  camera.aspect = 0.75*window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( 0.6*window.innerWidth, 0.8*window.innerHeight,false);

  render();

}

function render() {

  renderer.render( scene, camera );

}

