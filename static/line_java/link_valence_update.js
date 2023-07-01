function valence_link_changes(event, link__, slide_val){
    let link_valence;
     if ($(event.target).attr('data-line-style') === 'Solid'){
         link_valence = 'Solid'
     }
     else if ($(event.target).attr('data-line-style') === 'Dashed'){
         link_valence = 'Dashed'
     }
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