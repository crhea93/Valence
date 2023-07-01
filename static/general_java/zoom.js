$(document).ready(function(){
    let cam_div = $('#CAM_items');
    const cam_height_init = cam_div.css('min-height').replace(/[^-\d\.]/g, '')
        $('#btn_ZoomIn').click(
            function () {
                let cam_div = $('#CAM_items');
                if (currentZoom < 1.5) {
                    currentZoom += .1
                    //cam_div.css({'height': cam_height_init*currentZoom})
                    //cam_div.css('min-height', cam_div.css('min-height').replace(/[^-\d\.]/g, '')*currentZoom)
                    cam_div.animate({'zoom': currentZoom,
                        'min-height': cam_height_init/currentZoom+'px',
                        'max-height':cam_height_init/currentZoom+'px'},
                        );

                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                }
            });
        $('#btn_ZoomOut').click(
            function () {
                let cam_div = $('#CAM_items');
                if (currentZoom > 0.6) {
                    currentZoom -= .1
                    //cam_div.css({'height': cam_height_init*currentZoom})
                    //cam_div.css('min-height', cam_div.css('min-height').replace(/[^-\d\.]/g, '')*currentZoom)
                    cam_div.animate({'zoom': currentZoom,
                        'min-height': cam_height_init/currentZoom+'px',
                        'max-height': cam_height_init/currentZoom+'px'},
                        );

                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                }
            });
})