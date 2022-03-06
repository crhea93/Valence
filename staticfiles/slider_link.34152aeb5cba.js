 //---------------SLIDER CHANGES------------------//
 // This function changes the attributes of the link if the slider is used


 function slider_link_changes(event,link__,slide_val) {
         link__.removeClass();
         let link_valence = null; // Simply initialize
         if ($('#Link_Valence_option1').is(':checked')){
             link_valence = 'solid'
         }
         else {
             link_valence = 'dashed'
         }
         if (slide_val === '2') {
             link__.css('border','4px black '+ link_valence);
             link__.addClass('link ui-widget-content')
         } else if (slide_val === '1') {
            link__.css('border','3px black '+ link_valence);
            link__.addClass('link ui-widget-content')
         } else if (slide_val === '0') {
             link__.css('border','2px black '+ link_valence);
             link__.addClass('link ui-widget-content')
         }else {
             //default to neutral
            link__.css('border','2px black '+ link_valence);
             link__.addClass('link ui-widget-content')
         }

 }