//Read file from input button

//var materials = {
//    default_material: new THREE.MeshLambertMaterial({ side: THREE.DoubleSide })
//};

var model_file = document.getElementById('stl_file');

model_file.addEventListener('change', function (event) {

    var file = event.target.files[0];
    loadFile(file);

}); 

var loadFile = function (file) {

    var filename = file.name;
    var extension = filename.split('.').pop().toLowerCase();

    var reader = new FileReader();

    reader.addEventListener('progress', function (data) {

        if (data.lengthComputable) { //if size of file transfer is known
            var percentage = Math.round((data.loaded * 100) / data.total);
            console.log(percentage);
            statsNode.innerHTML = 'Loaded : ' + percentage + '%' + ' of ' + filename
            + '<br>'
            + '<progress value="0" max="100" class="progress"></progress>';
            $('.progress').css({ 'width': percentage + '%' });////Width of progress bar set to the current percentage of model loaded (progress bar therefore increases in width as model loads)
            $('.progress').val(percentage); //Set progress bar value to the current amount loaded
        }

    });

    switch (extension) {

        case 'stl':

            reader.addEventListener('load', function (event) {

                //When file type matches case - remove sample model or remove previously loaded model from user file
                //scene.remove(sample_model);
                //removeModel();
                //modelLoaded = true;
                
                var contents = event.target.result;
              
                try {
                    var geometry = new THREE.STLLoader(manager).parse(contents);
                    console.log(geometry);
                }
                catch (err) {
                    //Model fails to load due to parsing error
                    alert("Problem parsing file: " + filename + "\n\n" + "ERROR MESSAGE: " + err.message);
                }

				var material = new THREE.MeshPhongMaterial( { color: 0x0e2045, specular: 0x111111, shininess: 200 } );
                model = new THREE.Mesh(geometry, material);

                model.geometry.computeBoundingBox();
                size = model.geometry.boundingBox;
                trans_z = -size.min.z/5;
                console.log(size.max.x+size.min.x)
                console.log(size.max.y+size.min.y)
                trans_x = -(size.max.x+size.min.x)/10;
                trans_y = -(size.max.y+size.min.y)/10;
                model.position.set(trans_x, trans_y, trans_z);

				model.rotation.set( 0, 0, 0 );
				model.scale.set( 0.2, 0.2, 0.2 );
                scene.add(model);
				render();

            }, false);

            if (reader.readAsBinaryString !== undefined) {

                reader.readAsBinaryString(file);

            } else {

                reader.readAsArrayBuffer(file);
            }

            break;

        default:

            alert( 'Unsupported file format (' + extension +  ').' );

            break;
    }

};