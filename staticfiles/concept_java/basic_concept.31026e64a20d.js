//------------------BASIC CONCEPT BLOCK DEFINITION------------------------//
function def_concept(x,y,ct,note_hidden, note_value){
    let text_mtop;
    if (note_hidden === ''){
        text_mtop = 0.5
    }
    else {
        text_mtop = 1.5
    }
    def_concept_ret = '<div class="block card shadow-none ui-widget-content draggable ui-resizable rectangle"'+
                     'id="block_'+ct+'"'+
                    //'title="'+ct+'"'+
                    'data-modifiable="True"'+
                     'style="'+
                    'left:'+x+'px;' +
                    'top:'+y+'px; ' +
                    'z-index: 3;' +'">'+
                    '<i class="far fa-sticky-note note-block" style="padding-left:6.5rem" '+note_hidden+' title="'+note_value+'"></i>'+
                    '<div id="block_form_'+ct+'" class="card-body block-form concept_form" style="z-index: 4">'+
                      '<div class="form-row">'+
                          '<div class="form-group">'+
                            '<input class="col-md-10" type="text" id="title_'+ct+'" placeholder="text" style="z-index: 5">'+
                          '</div></div>'+
                        '<div class="slider custom-range" id="shape_' + ct + '" value="3"></div>' +
                        '<input type="checkbox" class="col-md-2 checkbox Ambivalence" id="check_' + ct + '" value="Ambivalent">' +
                     '</div>' +
                    '<div class="success_blk" style="text-align:center;z-index:3;margin-top: '+text_mtop+'rem;margin-left:0.75rem;margin-right: 0.75rem" id="success_block_'+ct+'"></div>'+
                    '</div>';
    return def_concept_ret
}