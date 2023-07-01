let drag_left = null;
let drag_top = null;
var pageTop = self.pageTop;
var pageLeft = self.pageLeft;
$(document).ready(function() {
        var self = {};
        $('#CAM_items').on('mousedown', function(e) {
            self.panStartX = e.pageX;
            self.panStartY = e.pageY;
            self.mouseDown = true;
            self.pageTop = parseInt($(this).css('top'), false) || 0;
            self.pageLeft = parseInt($(this).css('left'), false) || 0;
        }).on('mousemove', function(e) {
            if (self.mouseDown) {

                self.panEndX = e.pageX;
                self.panEndY = e.pageY;
                //------------- UP DOWN MOVEMENT -----------------------//
                if (self.panStartY > self.panEndY) {
                    self.panTop = self.panEndY - self.panStartY;
                    pageTop+= self.panTop;
                    if (pageTop > $('#CAM_items').top) pageTop = $('#CAM_items').top; // needs to be calculated to top of #CAM_items
                    $(this).css({ top: pageTop });
                } else {
                    // Down
                    self.panTop = self.panStartY - self.panEndY;
                    pageTop-= self.panTop;
                    $(this).css({ top: pageTop });
                }
                //------------ LEFT RIGHT MOVEMENT ------------//
                if (self.panStartX > self.panEndX) {
                    self.panLeft = self.panEndX - self.panStartX;
                    pageLeft += self.panLeft;
                    if (pageLeft > $('#CAM_items').left) pageLeft = $('#CAM_items').left; // needs to be calculated to left edge of #CAM_items
                    $(this).css({ left: pageLeft });
                } else {
                    // Down
                    self.panLeft = self.panStartX - self.panEndX;
                    pageLeft -= self.panLeft;
                    $(this).css({ left: pageLeft });
                }
            }
        }).on('mouseup', function(e) {
            self.mouseDown = false;
            shift_left_total += pageLeft;
            shift_top_total += pageTop;
        });
    });