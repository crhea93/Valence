//-------------------------------------------------------------------------//
// Script to update existing links while dragging a concept
//-------------------------------------------------------------------------//

function update_link_start(link_sel){
    let end_block = $('[data-title='+"'"+link_sel.attr('data-end_id')+"']");
    let start_block = $('[data-title='+"'"+link_sel.attr('data-start_id')+"']");
    let starty = start_block.css('top');//  ui_pos_left.split('px')[[0]]; //link_sel.css('left');
    let startx = start_block.css('left');//ui_pos_top.split('px')[0]; //link_sel.css('top');
    let endx = end_block.css('left');//link_sel.attr('data-right');
    let endy = end_block.css('top');//link_sel.attr('data-bottom');
    if (endx < startx) {
        var temp = endx;
        endx = startx;
        startx = temp;
        temp = endy;
        endy = starty;
        starty = temp;
    }

    let link_id = link_sel.attr('id');
    let link_old = $('#'+link_id);
    let arrow_type = '';

    if (link_old.hasClass('none')){
        arrow_type = 'none';
    }
    else if (link_old.hasClass('uni')){
        arrow_type = 'uni'
    }
    else if (link_old.hasClass('bi')){
        arrow_type = 'bi'
    }
    let link_style = line_style_func(link_sel);
    // New Link
    const new_link = createLine(link_id,link_id,[startx,starty,endx,endy],link_sel.attr('data-start_id'),link_sel.attr('data-end_id'),link_style+' '+arrow_type);
    link_old.remove();
    $("#CAM_items").append(new_link);

}

function update_link_end(link_sel){
    let start_block = $('[data-title='+"'"+link_sel.attr('data-start_id')+"']");
    let end_block = $('[data-title='+"'"+link_sel.attr('data-end_id')+"']");
    let endy = end_block.css('top');//ui_pos_left.split('px')[[0]]; //link_sel.css('left');
    let endx = end_block.css('left');//ui_pos_top.split('px')[0]; //link_sel.css('top');
    let startx = start_block.css('left');//link_sel.attr('data-right');
    let starty = start_block.css('top');//link_sel.attr('data-bottom');
    if (endx > startx) {
        var temp = startx;
        startx = endx;
        endx = temp;
        temp = starty;
        starty = endy;
        endy = temp;
    }
    let link_id = link_sel.attr('id');
    let link_old = $('#'+link_id);
    let arrow_type = '';

    if (link_old.hasClass('none')){
        arrow_type = 'none';
    }
    else if (link_old.hasClass('uni')){
        arrow_type = 'uni'
    }
    else if (link_old.hasClass('bi')){
        arrow_type = 'bi'
    }
     let link_style = line_style_func(link_sel);//;link_sel.css('border').split(' ')[1];
    // New Link
    var new_link = createLine(link_id,link_id,[startx,starty,endx,endy],link_sel.attr('data-start_id'),link_sel.attr('data-end_id'),link_style+' '+arrow_type);
    link_old.remove();
    $("#CAM_items").append(new_link);

}