function createLine(line_num,name,point_array,drag_height,drag_width,start_block_id,end_block_id,Add_class){
    //line_num,name,point_array,drag_height,drag_width,line_style,line_width,start_block_id,end_block_id,Add_class
  x1 = point_array[0]; x2 = point_array[2];
  x1 = parseFloat(x1); x2 = parseFloat(x2);
  y1 = point_array[1]; y2 = point_array[3];
  y1 = parseFloat(y1); y2 = parseFloat(y2);
  var width = drag_width;
  var height=  drag_height;
  // Need to make sure the line is pointing in the right direction
  if (x2 < x1) {
        var temp = x1;
        x1 = x2;
        x2 = temp;
        temp = y1;
        y1 = y2;
        y2 = temp;
  }
  var length = Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
  var angle = Math.atan((y2 - y1) / (x2 - x1));
  var left_ = x1 + 1.5*width  - 0.5 * (length) * (1 - Math.cos(angle));
  var top_ = y1 - 0.5*height  + 0.5 * (length) * Math.sin(angle) ;
  var transform = 'rotate('+angle+'rad)';
  let hidden_arrow = 'hidden'; let hidden_arrow2 = 'hidden';
  let line = '';
  if (~Add_class.indexOf("uni")){
      // Need to make sure the arrow (if there is one and only one) is pointing from the starting to the ending block
      const start_block = $('#block_'+start_block_id);
      const end_block = $('#block_'+end_block_id);
      // Check which block is to the left
      if (parseFloat(start_block.css('left')) < parseFloat(end_block.css('left'))){
            hidden_arrow = '';
            let line = '<div class="link ui-widget-content '+ ' ' +Add_class+
                '" id="' + name + '"'+
              'style="position:absolute;transform:'+transform+';' +
              'width:'+(length-180)+ 'px;'+
              'height:10px;'+
              'left:'+(left_+100)+'px;'+
              'top:'+(top_)+'px;'+
                ';z-index: 1;"'+
                ' data-right="'+x2+'"'+
                ' data-bottom="'+y2+'"'+
                ' data-start_id="'+start_block_id+'"'+
                ' data-end_id="'+end_block_id+'"'+
                '>'+
                '<div class="arrow" '+hidden_arrow+' style="left:'+(-10)+'px;top:'+(-22.5)+'px"></div>'+
                '<div class="arrow2" '+hidden_arrow2+' style="top:'+(-22.5)+'px'+
                    ';left:'+(length)+'px;'+
                '"></div>'+
                '</div>';
            return line;
      }
      else {
          hidden_arrow2 = '';
          let line = '<div class="link ui-widget-content '+ ' ' +Add_class+
                '" id="' + name + '"'+
              'style="position:absolute;transform:'+transform+';' +
              'width:'+(length-150)+ 'px;'+
              'height:10px;'+
              'left:'+(left_+50)+'px;'+
              'top:'+(top_)+'px;'+
                ';z-index: 1;"'+
                ' data-right="'+x2+'"'+
                ' data-bottom="'+y2+'"'+
                ' data-start_id="'+start_block_id+'"'+
                ' data-end_id="'+end_block_id+'"'+
                '>'+
                '<div class="arrow" '+hidden_arrow+' style="left:'+(-10)+'px;top:'+(-22.5)+'px"></div>'+
                '<div class="arrow2" '+hidden_arrow2+' style="top:'+(-22.5)+'px'+
                    ';left:'+(length-160)+'px;'+
                '"></div>'+
                '</div>';
          return line;
      }
  }
  else if (~Add_class.indexOf("bi")){
      hidden_arrow = '';
      hidden_arrow2 = '';
      return line;
  }
  else{
      // No arrow
      let line = '<div class="link ui-widget-content '+ ' ' +Add_class+
                '" id="' + name + '"'+
              'style="position:absolute;transform:'+transform+';' +
              'width:'+(length)+ 'px;'+
              'height:10px;'+
              'left:'+(left_)+'px;'+
              'top:'+(top_)+'px;'+
                ';z-index: 1;"'+
                ' data-right="'+x2+'"'+
                ' data-bottom="'+y2+'"'+
                ' data-start_id="'+start_block_id+'"'+
                ' data-end_id="'+end_block_id+'"'+
                '>'+
                '<div class="arrow" '+hidden_arrow+' style="left:'+(-10)+'px;top:'+(-22.5)+'px"></div>'+
                '<div class="arrow2" '+hidden_arrow2+' style="top:'+(-22.5)+'px'+
                    ';left:'+(length-100)+'px;'+
                '"></div>'+
                '</div>';
      return line;
  }


}