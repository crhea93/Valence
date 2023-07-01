 //---------------SLIDER CHANGES------------------//
 function slider_changes() {
     //$(event.target).select()
     //let slider_elem = $('#shape_'+ct);
     //let block__ = $('#block_'+ct);
     $('.slider').slider({
         //value: $(this).val(),
         step: 1,
         min: 0,
         max: 6,
         create: function() {

          },
         slide: function(event, ui){

         },
         stop: function (event, ui) {
             let slide_val = ui.value;
             ct = $(this).attr('id').split('_')[1];
             let block__ = $('#block_'+ct);
             block__.removeClass();
             if (slide_val === 0) {
                 block__.addClass('block card shadow-none draggable ui-widget-content hexagonNegStrong Open');
                 $(this).attr('value', 0);
             } else if (slide_val === 1) {
                 block__.addClass('block card shadow-none draggable ui-widget-content hexagonNeg Open');
                 $(this).attr('value', 1);
             } else if (slide_val === 2) {
                 block__.addClass('block card shadow-none draggable ui-widget-content hexagonNegWeak Open');
                 $(this).attr('value', 2);
             } else if (slide_val === 3) {
                 block__.addClass('block card shadow-none draggable ui-widget-content rectangle Open');
                 $(this).attr('value', 3);
             } else if (slide_val === 4) {
                 block__.addClass('block card shadow-none draggable ui-widget-content  rounded-circle-weak Open');
                 $(this).attr('value', 4);
             } else if (slide_val === 5) {
                 block__.addClass('block card shadow-none draggable ui-widget-content rounded-circle-normal Open');
                 $(this).attr('value', 5);
             }  else if (slide_val === 6) {
                 block__.addClass('block card shadow-none draggable ui-widget-content  rounded-circle-strong Open');
                 $(this).attr('value', 6);

             } else {
                 block__.addClass('block card shadow-none draggable ui-widget-content hexagonAmb hexagonAmbCircle Open') //default to neutral
             }
         }
 })
 };

