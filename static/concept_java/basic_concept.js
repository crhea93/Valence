 //------------------BASIC CONCEPT BLOCK DEFINITION------------------------//
function def_concept(x,y,ct,note_hidden, note_value){
    let text_mtop;
    if (note_hidden === ''){
        text_mtop = 0.5
    }
    else {
        text_mtop = 0.5
    }
    def_concept_ret = '<div class="block card shadow-none ui-widget-content draggable rectangle align-middle text-center mb-0"'+
                     'id="block_'+ct+'"'+
                    //'title="'+ct+'"'+
                    'data-modifiable="True"'+
                     'style="'+
                    'left:'+x+'px;' +
                    'top:'+y+'px; ' +
                    'z-index: 3;' +'">'+
                    '<span class="position-absolute">' +
                    '  <i class="far fa-comment-dots" '+note_hidden+' title="'+note_value+'"></i>'+
                    '</span>'+
                    '<div id="block_form_'+ct+'" class="card-body block-form concept_form" style="z-index: 4">'+
                      '<div class="form-row">'+
                          '<div class="form-group">'+
                            '<input class="col-md-10" type="text" placeholder="text" id="title_'+ct+'" maxlength="50" style="z-index: 5">'+
                          '</div></div>'+
                        '<div class="slider custom-range" id="shape_' + ct + '" value="3"></div>' +
                        '<input type="checkbox" class="col-md-2 checkbox Ambivalence" id="check_' + ct + '" value="Ambivalent" title="Ambivalent">' +
                     '</div>' +
                    '<div class="flex success_blk align-items-center text-center h-100" style="z-index:3" id="success_block_'+ct+'"></div>'+
                    '</div>';
    return def_concept_ret
}
