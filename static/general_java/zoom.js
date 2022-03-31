$(document).ready(function(){
    let cam_div = $('#CAM_items').children();
        $('#btn_ZoomIn').click(
            function () {
                if (currentZoom < 1.5) {
                    cam_div.animate({'zoom': currentZoom += .1,},
                        {'height': cam_div.height+100, 'width': cam_div.width+100},
                        {});
                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                }
            });
        $('#btn_ZoomOut').click(
            function () {
                if (currentZoom > 0.6) {
                    cam_div.animate({'zoom': currentZoom -= .1,},
                        {'height': cam_height_max*(1/currentZoom)},
                        {});
                    $('#zoom_lev').html('Zoom: '+currentZoom.toFixed(1));
                }
            });
})