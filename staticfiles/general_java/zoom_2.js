$(document).ready(function(){
    let cam_div = $('#CAM_items');
        $('#btn_ZoomIn').click(
            function () {
                if (currentZoom < 1.5) {
                    let cam_width_prev = cam_div.css('width').trim('px');
                    cam_div.animate({'zoom': currentZoom += .1,
                        'height': cam_height_max*(1/currentZoom)}, {
                        /*start: function () {
                            let cam_width_curr = $('#CAM_items').css('width').trim('px');
                             let cam_width_dif = parseFloat(cam_width_curr) - parseFloat(cam_width_prev);
                             console.log(parseFloat(cam_width_curr)/parseFloat(cam_width_prev));
                            $('.block').each(function () {
                                // Move the blocks
                                let curr_left = parseFloat($(this).css('left').trim('px'));
                                $(this).css('left', 0.9*curr_left)
                                // Now update the block
                                //console.log('closing block')
                                close_block_func(this)
                            });
                            $('.link').each(function () {
                                let curr_left = parseFloat($(this).css('left').trim('px'));
                                $(this).css('left', 0.9*curr_left)
                                update_link($(this))
                            });
                        }*/
                         });
                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                }
            });
        $('#btn_ZoomOut').click(
            function () {
                if (currentZoom > 0.6) {
                    cam_div.animate({'zoom': currentZoom -= .1,
                        'height': cam_height_max*(1/currentZoom)},{
                        /*start: function() {
                            let cam_width_curr = parseFloat($('#CAM_items').css('width').trim('px'));
                            //console.log('curr width:'+cam_width_curr);
                            //let cam_width_dif = parseFloat(cam_width_curr) - parseFloat(cam_width_prev)
                            //console.log('new width: '+cam_width_dif)
                            console.log(parseFloat(cam_width_curr)/parseFloat(cam_width_prev))
                            console.log(currentZoom)
                          $('.block').each(function(){
                                let curr_left = parseFloat($(this).css('left').trim('px'));
                                $(this).css('left',1.1*curr_left)
                                close_block_func(this)
                            });
                            $('.link').each(function () {
                                let curr_left = parseFloat($(this).css('left').trim('px'));
                                //$(this).css('left', 1.1*curr_left)
                                update_link($(this))
                                $(this).remove()
                            });
                        }*/
                    });
                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                    //console.log('new width:'+$('#CAM_items').css('width'))

                }
            });
})