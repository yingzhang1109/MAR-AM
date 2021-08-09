if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var camera, scene, renderer;
console.log(name)
init();

function init() {

  scene = new THREE.Scene();
  scene.add( new THREE.AmbientLight( 0x999999 ) );

  camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.1, 500000 );

  // Z is up for objects intended to be 3D printed.

  //camera.up.set( 0, 0, 1 );
  camera.position.set( 0, 0, 20 );

  camera.add( new THREE.PointLight( 0xffffff, 0.8 ) );

  scene.add( camera );

  var grid = new THREE.GridHelper( 25, 50, 0xffffff, 0x555555 );
  grid.rotateOnAxis( new THREE.Vector3( 1, 0, 0 ), 90 * ( Math.PI/180 ) );
  scene.add( grid );

  renderer = new THREE.WebGLRenderer( { canvas: document.querySelector('#canvas2') } );
  renderer.setClearColor( 0x999999 );
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( 0.5*window.innerWidth, 0.5*window.innerHeight );
  document.body.appendChild( renderer.domElement );

  var loader = new THREE.STLLoader();


  // Binary files

  var material = new THREE.MeshPhongMaterial( { color: 0x0e2045, specular: 0x111111, shininess: 200 } );
  loader.load( '../static/saved/'+name, function ( geometry ) {
    var mesh = new THREE.Mesh( geometry, material );
    mesh.geometry.computeBoundingBox();
    size = mesh.geometry.boundingBox;
    trans = -size.min.z/5;
    mesh.position.set( 0, 0, trans );
    mesh.rotation.set( 0, 0, 0 );
    mesh.scale.set( .2, .2, .2 );

    mesh.castShadow = true;
    mesh.receiveShadow = true;

    scene.add( mesh );
    render();
  });

  var controls = new THREE.OrbitControls( camera, renderer.domElement );
  controls.addEventListener( 'change', render );
  controls.target.set( 0, 1.2, 2 );
  controls.update();
  window.addEventListener( 'resize', onWindowResize, false );

}

function onWindowResize() {

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( 0.5*window.innerWidth, 0.5*window.innerHeight );

  render();

}

function render() {

  renderer.render( scene, camera );

}
