function existing_concept_init(title,x,y,shape,num,id) {
    num = parseInt(num);
    var class_shape = '';
    var background_shape = '';
    var border_shape = '';
    var border_strength = '';
    console.log(shape);
     if (shape === 'negative strong') {
         class_shape = 'hexagonNegStrong';
         background_shape = 'rgba(255, 148, 120, 1)';
         border_shape = 'red';
         border_strength = '6px';
     } else if (shape === 'negative') {
        class_shape = 'hexagonNeg';
        background_shape = 'rgba(255, 148, 120, 1)';
        border_shape = 'red';
        border_strength = '3px';
    } else if (shape === 'neutral') {
        class_shape = 'rectangle';
        background_shape = 'rgba(255, 255, 204, 1)';
        border_shape = 'yellow';
        border_strength = '3px';
    } else if (shape === 'positive') {
        class_shape = 'rounded-circle';
        background_shape = 'rgba(134, 226, 213, 1)';
        border_shape = 'green';
        border_strength = '3px';
    } else if (shape === 'positive strong') {
         class_shape = 'rounded-circle';
         background_shape = 'rgba(134, 226, 213, 1)';
         border_shape = 'green';
         border_strength = '6px';
     }else {
         class_shape = 'hexagonAmb';
        //class_shape = 'clip-each border-style-thin-amb fill-hex-amb';//'hexagon rectangle';
        background_shape = '#D165FF';
        border_shape = '#D165FF';
        border_strength = '3px';
    }
    //Create concept already in user's bank
    var def_created_concept = '<div class="block card draggable ui-widget-content ' + class_shape + '"' +
        'id="block_' + num + '"' +
        'style="' +
        'width:150px;' +
        'height:100px;' +
        'left:' + x + 'px;' +
        'top:' + y + 'px;' +
        'background:' + background_shape + ';' +
        'border: '+border_strength+' solid ' + border_shape + ';' +

        'text-align:center;position:absolute'+

        ';z-index: 2;"' +

        'title="' + id + '">' +
        '<button type="button" class="close" aria-label="Close">\n' +
        '          <span class="float-right" style="font-size:1rem" aria-hidden="true" id="delete_' + num + '" >&times;</span>\n' +
        '        </button>' +
        '<div id="block_form_' + num + '" class="card-body block-form" hidden>' +
        '<div class="form-row">' +
        '<div class="form-group">' +
        '<input class="col-md-10" type="text" style="z-index: 2" id="title_' + num + '" value="'+title+'" placeholder="text">'+
        '</div></div>' +
        '<div class="form-row">' +
        '<div class="form-group">' +
        '<input type="range" class="slider col-md-8" min="0" max="4" id="shape_' + num + '">' +
        '<input  type="checkbox" class="col-md-2 checkbox" id="check_' + num + '" value="Ambivalent">' +
        '</div>' +

        '</div>' +
        '</div>' +
        '<div class="text-align:center;vertical-align:middle" style="z-index: 3" id="success_block_' + num + '"></div>' +
        '</div>';

     // If the concept is checked, check the ambivalent box
    if ($('#block_'+num).hasClass('hexagonAmb')){
        $('#check_' + num).prop('checked', true)
    }
    return def_created_concept
}