 //---------------SLIDER CHANGES------------------//
 function slider_changes(event,ct) {
         let slider_elem = $('#shape_'+ct);
         let block__ = $('#block_'+ct);
         let slide_val = slider_elem.val();
         slide_val = slider_elem.val();
         block__.removeClass();
         if (slide_val === '0') {
             block__.addClass('block card draggable ui-widget-content hexagonNegStrong Open');
             block__.css('background', '#FF9478');
             block__.css('border-color', '#ff0000');
             block__.css('border-width', '6px')
         } else if (slide_val === '1') {
             block__.addClass('block card draggable ui-widget-content hexagonNeg Open');
             block__.css('background', '#FF9478');
             block__.css('border-color', '#ff0000');
             block__.css('border-width', '3px')
         } else if (slide_val === '2') {
             block__.addClass('block card draggable ui-widget-content rectangle Open');
             block__.css('background', 'rgba(255, 255, 204, 1)');
             block__.css('border-color', 'yellow');
             block__.css('border-width', '3px')
         } else if (slide_val === '3') {
             block__.addClass('block card draggable ui-widget-content rounded-circle Open');
             block__.css('background', 'rgba(134, 226, 213, 1)');
             block__.css('border-color', 'green');
             block__.css('border-width', '3px')
         } else if (slide_val === '4') {
             block__.addClass('block card draggable ui-widget-content rounded-circle strong Open');
             block__.css('background', 'rgba(134, 226, 213, 1)');
             block__.css('border-color', 'green');
             block__.css('border-width', '6px')
         } else {
             //default to neutral
             block__.addClass('block card draggable ui-widget-content rectangle Open');
             block__.css('background', 'rgba(255, 255, 204, 1)');
             block__.css('border-color', 'yellow')
         }
     slider_elem.slider({
         stop: function (event, ui) {
             var slide_val = slider_elem.val();
             block__.removeClass();
             if (slide_val === '0') {
                 block__.addClass('block card draggable ui-widget-content hexagonNegStrong Open')
             } else if (slide_val === '1') {
                 block__.addClass('block card draggable ui-widget-content hexagonNeg Open')
             } else if (slide_val === '2') {
                 block__.addClass('block card draggable ui-widget-content rectangle Open')
             } else if (slide_val === '3') {
                 block__.addClass('block card draggable ui-widget-content rounded-circle Open')
             } else if (slide_val === '4') {
                 block__.addClass('block card draggable ui-widget-content rounded-circle strong Open')
             } else {
                 block__.addClass('block card draggable ui-widget-content hexagonAmb Open') //default to neutral
             }
         }
 })
 };