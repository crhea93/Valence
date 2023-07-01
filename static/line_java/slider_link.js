 //---------------SLIDER CHANGES------------------//
 // This function changes the attributes of the link if the slider is used

 function slider_link_update_func(link__,slide_val,arrow_type){
    const link_classes = link__.attr('class').split(/\s+/);
    link__.removeClass();
     // Valence Calculations
     let link_valence = null; // Simply initialize
    //
     if (~link_classes.indexOf("Solid") || ~link_classes.indexOf("Solid-Strong") || ~link_classes.indexOf("Solid-Weak")){
         link_valence = 'Solid';
     }
     else if (~link_classes.indexOf("Dashed") || ~link_classes.indexOf("Dashed-Strong") || ~link_classes.indexOf("Dashed-Weak")){
         link_valence = 'Dashed';
     }
     else {
         link_valence = '---';
     }
     console.log(link_valence)
    // Update Strength According to slider
     if (slide_val === '2') {
         //link__.css('border','4px black '+ link_valence);
         link_valence += '-Strong'; // Add strong since we have Strong-Strength
         link__.addClass('link ui-widget-content '+ link_valence + ' ' + arrow_type)
     } else if (slide_val === '1') {
        //link__.css('border','3px black '+ link_valence);
         // Don't add any Strength
        link__.addClass('link ui-widget-content '+ link_valence + ' '+ arrow_type)
     } else if (slide_val === '0') {
         //link__.css('border','2px black '+ link_valence);
         link_valence += '-Weak'; // Add weak since we have Weak-Strength
         link__.addClass('link ui-widget-content '+ link_valence + ' '+ arrow_type)
     }else {
         //default to neutral
        //link__.css('border','2px black '+ link_valence);
         link__.addClass('link ui-widget-content '+ link_valence + ' '+arrow_type)
     }
 }

 function slider_link_changes(event,link__,slide_val) {
        let arrow_type = 'none';
        if (link__.hasClass('none')){
             arrow_type = 'none'
         }
         else if (link__.hasClass('uni')){
             arrow_type = 'uni'
         }
         else if (link__.hasClass('bi')){
             arrow_type = 'bi'
         }
         else{
             // Set to current value
             arrow_type = 'none'//link__.css('border').split(" ")[1]
         }
        slider_link_update_func(link__,slide_val,arrow_type)
 }