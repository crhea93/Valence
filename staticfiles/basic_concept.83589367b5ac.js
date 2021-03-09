//------------------BASIC CONCEPT BLOCK DEFINITION------------------------//
function def_concept(x,y,ct){
    def_concept_ret = '<div class="block card ui-widget-content draggable ui-resizable rectangle"'+
                     'id="block_'+ct+'"'+
                     'style="'+
                    'width:150px;'+
                    'height:100px;'+
                    'left:'+x+'px;' +
                    'top:'+y+'px;' +
                    'background:rgba(255, 255, 204, 1);'+
                    'border: 3px solid yellow;'+
                    'text-align:center;position:absolute;'+

                        'z-index: 2;' +'">'+
                    '<button type="button" class="close" style="z-index: 2" aria-label="Close">\n' +
                    '<span class="float-right close-btn" style="font-size:1rem" aria-hidden="true" style="z-index: inherit" id="delete_'+ct+'">&times</span>\n' +
                    '</button>'+
                    '<div id="block_form_'+ct+'" class="card-body block-form">'+
                      '<div class="form-row">'+
                          '<div class="form-group">'+
                            '<input class="col-md-10" type="text" id="title_'+ct+'" placeholder="text">'+
                          '</div></div>'+
                      '<div class="form-row">'+
                          '<div class="form-group">'+
                            '<input type="range" class="slider col-md-8" min="0" max="4" id="shape_'+ct+'">'+
                            '<input  type="checkbox" class="col-md-2 checkbox" id="check_'+ct+'" value="Ambivalent">' +
                          '</div>'+

                      '</div>'+
                     '</div>' +
                    '<div style="text-align:center;z-index:3" id="success_block_'+ct+'"></div>'+
                    '</div>';
    return def_concept_ret
}