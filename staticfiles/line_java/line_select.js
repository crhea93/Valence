
var DELAY_link = 200, clicks_link = 0, timer_link = null;
var ctrl_clicks_link = 0; //Number of control clicks

function line_set_func(link__){
    let slider_set;
     const link_classes = link__.attr('class').split(/\s+/);
     if (~link_classes.indexOf("Dashed-Weak") || ~link_classes.indexOf("Solid-Weak")) {
         slider_set = 0;
     }
     else if (~link_classes.indexOf("Dashed") || ~link_classes.indexOf("Solid")) {
         slider_set = 1;
     }
     else if (~link_classes.indexOf("Dashed-Strong") || ~link_classes.indexOf("Solid-Strong")) {
         slider_set = 2;
     }
     return slider_set
}

function line_set_val_func(link__){
    // Function to set the correct button for the valence when a line is selected
    const link_classes = link__.attr('class').split(/\s+/);
    if (~link_classes.indexOf("Solid") || ~link_classes.indexOf("Solid-Strong") || ~link_classes.indexOf("Solid-Weak")){
         $('#Link_Valence_option1').parent().addClass('active');
         $('#Link_Valence_option2').parent().removeClass('active');
     }
     else if (~link_classes.indexOf("Dashed") || ~link_classes.indexOf("Dashed-Strong") || ~link_classes.indexOf("Dashed-Weak")){
        $('#Link_Valence_option2').parent().addClass('active');
        $('#Link_Valence_option1').parent().removeClass('active');
     }
}

function line_set_arrow_func(link__){
    // Function to set the correct button for the arrow when a line is selected
     const link_classes = link__.attr('class').split(/\s+/);
    if (~link_classes.indexOf("none")){
         $('#arrow_option1').parent().addClass('active');
         $('#arrow_option2').parent().removeClass('active');
     }
     else if (~link_classes.indexOf("uni")){
        $('#arrow_option1').parent().removeClass('active');
        $('#arrow_option2').parent().addClass('active');
     }
}


$(document).on("click", '.link',function(e){
    var target_el = $(this); //get link
    click_element = 'link';
    $('.block.Open').each(function(){
        close_block_func(this);
      });
    clicks_link++;  //count clicks
    if (clicks_link === 1) { //Single Click
        timer_link = setTimeout(function () {
            // Close all currently opened links
            $('.Selected-link').each(function(){
               $(this).removeClass('Selected-link');
                $(this).children().each(function(){
                    $(this).removeClass('Selected-arrow')
                })
            });
            $('.Selected').each(function(){
               $(this).removeClass('Selected')
            });
            target_el.addClass('Selected-link');
            target_el.children().each(function(){
                $(this).addClass('Selected-arrow')
             })
            $('#Link_Info').attr('hidden', false);
            $("#No_Link_Info").attr('hidden', true);
            // Set link slider choice
            $("#link_slider_choice").val(line_set_func(target_el));
            // Set Valence button
            line_set_val_func(target_el);
            // Set Arrow button
            line_set_arrow_func(target_el);
            clicks_link = 0;
        }, DELAY_link);// End Single Click
    } else { //Double Click
        clearTimeout(timer_link);    //prevent single-click action
        // Close all currently opened links
            $('.Selected-link').each(function(){
               $(this).removeClass('Selected-link');
                $(this).children().each(function(){
                    $(this).removeClass('Selected-arrow')
                })
            });
        target_el.addClass('Selected-link');
        // Add selected arrow
        target_el.children().each(function(){
            $(this).addClass('Selected-arrow')
        })
        clicks_link = 0;             //after action performed, reset counter
    }//End Double Click

})
.on("dblclick", '.block',function(e){
    e.preventDefault();  //cancel system double-click event
});

function valence_link_changes(event, link__, slide_val){
    let link_valence;
    //console.log($(event.target).text().trim())
    let arrow_type = 'none';
    if (link__.hasClass('none')){
         arrow_type = 'none'
     }
     else if (link__.hasClass('uni')){
         arrow_type = 'uni'
        link__.children().each(function(){
            $(this).addClass('Selected-arrow');
        })
     }
     else{
         // Set to current value
         arrow_type = 'none'
     }
    link__.removeClass();
     console.log($(event.target))//.children().attr('id'))
     if ($(event.target).children().attr('id') === 'Link_Valence_option1'){
         link_valence = 'Solid'
     }
     else if ($(event.target).children().attr('id') === 'Link_Valence_option2'){
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


$(document).on('mouseup', '#Link_Valence', function (event) {
    event.stopPropagation();
    var target_el = $('.Selected-link').first();
    valence_link_changes(event, target_el, $('#link_slider_choice').val());
    update_link_form_slider(target_el, $('#link_slider_choice').val());
    $(target_el).children().each(function(){
            $(this).addClass('Selected-arrow')
        })
});

$(document).on('mouseup','#link_slider_choice',function (event) {
        // submit change
        var target_el = $('.Selected-link').first();
        slider_link_changes(event, target_el, $(this).val());
        update_link_form_slider(target_el, $(this).val());
        target_el.addClass('Selected-link')
        $(target_el).children().each(function(){
            $(this).addClass('Selected-arrow')
        })
});


function arrow_changes(event, link__, slide_val){
    let arrow_type = $(event.target).children('input').attr('id');
    if (arrow_type === 'arrow_option1'){
         arrow_type = 'none'
     }
     else if (arrow_type === 'arrow_option2'){
         arrow_type = 'uni'

     }
     else{
         // Set to current value
         arrow_type = 'none'//link__.css('border').split(" ")[1]
     }
     const link_classes = link__.attr('class').split(/\s+/);
     link__.removeClass();
     let link_valence = null; // Simply initialize
    //
     if (~link_classes.indexOf("Solid") || ~link_classes.indexOf("Solid-Strong") || ~link_classes.indexOf("Solid-Weak")){
         link_valence = 'Solid';
     }
     else if (~link_classes.indexOf("Dashed") || ~link_classes.indexOf("Dashed-Strong") || ~link_classes.indexOf("Dashed-Weak")){
         link_valence = 'Dashed';
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

     link__.addClass('Selected-Link');
    $(link__).children().each(function(){
            $(this).addClass('Selected-arrow')
        })
     console.log('arrows')

}

$(document).on('mouseup', '#arrow_type', function (event) {
    event.stopPropagation();
    var target_el = $('.Selected-link').first();
    arrow_changes(event, target_el, $('#link_slider_choice').val());
    update_link_form_slider(target_el, $('#link_slider_choice').val());
    $(target_el).children().each(function(){
            $(this).addClass('Selected-arrow')
        })
});