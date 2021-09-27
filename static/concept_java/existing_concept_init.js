function existing_concept_init(title,x,y,width,height,text_scale,shape,num,note_hidden,note_value,modifiable) {
    num = parseInt(num);
    var class_shape = '';
    var slide_val = 0;
     if (shape === 'negative strong') {
         class_shape = 'hexagonNegStrong';
         slide_val = 0;
     } else if (shape === 'negative') {
        class_shape = 'hexagonNeg';
        slide_val = 1;
    } else if (shape === 'negative weak') {
        class_shape = 'hexagonNegWeak';
        slide_val = 2;
    } else if (shape === 'neutral') {
        class_shape = 'rectangle';
        slide_val = 3;
    } else if (shape === 'positive weak') {
        class_shape = 'rounded-circle-weak';
        slide_val = 4;
    } else if (shape === 'positive') {
        class_shape = 'rounded-circle-normal';
        slide_val = 5;
    } else if (shape === 'positive strong') {
         class_shape = 'rounded-circle-strong';
         slide_val = 6;
     }else {
         class_shape = 'hexagonAmb hexagonAmbCircle';

    }
    //Create concept already in user's bank
    var def_created_concept = '<div class="block shadow-none card resizable draggable ui-widget-content ' + class_shape + ' text-center align-middle mb-0"' +
        'id="block_' + num + '"' +
        'style="' +
        'left:' + x + 'px;' +
        'top:' + y + 'px;' +
        'width:' + width + 'px;' +
        'height:' + height + 'px;' +
        'text-align:center;position:absolute'+
        ';z-index: 3;"' +
        'data-title="' + num + '" ' +
        'data-modifiable="' + modifiable + '"' +
        '>' +
        '<span class="fa-stack fa-sm" title="'+note_value+'">' +
        '  <i class="far fa-comment-dots" '+note_hidden+' title="'+note_value+'"></i>'+
        '</span>'+
        '<div id="block_form_' + num + '" class="card-body block-form concept_form" hidden>' +
            '<div class="form-row">' +
                '<div class="form-group">' +
                    '<input class="col-md-10" type="text" placeholder="text" id="title_' + num + '"  value="'+title+'" maxlength = "50" >'+
                '</div>'+
            '</div>' +
        '<div class="slider custom-range" id="shape_' + num + '" value="' + slide_val + '"></div>' +
        '   <input type="checkbox" class="col-md-2 checkbox Ambivalence" id="check_' + num + '" value="Ambivalent" title="Ambivalent">' +
        '</div>' +
        '<div class="success_blk align-middle text-center" style="z-index: 3; font-size:'+text_scale+'px" id="success_block_' + num + '"></div>' +
        '</div>';
    return def_created_concept
}
