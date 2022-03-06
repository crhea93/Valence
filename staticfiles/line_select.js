
var DELAY_link = 200, clicks_link = 0, timer_link = null;
var ctrl_clicks_link = 0; //Number of control clicks



$(document).on("click", '.link',function(e){
    var target_el = $(this); //get link
    click_element = 'link';
    $('.block.Open').each(function(){
        close_block_func(this);
      });
    clicks_link++;  //count clicks
    if (clicks_link === 1) { //Single Click
        timer_link = setTimeout(function () {
            target_el.addClass('Selected-link');
            $('#Link_Info').attr('hidden', false);
            $("#No_Link_Info").attr('hidden', true);
            $("#link_slider_choice").val(parseFloat(target_el.css('border').split(' ')[0][0]) - 2);
            if ($("#Link_Toggle").val(target_el.css('border').split(' ')[2]) === 'solid'){
                $('#Link_Valence_option1').prop('checked', true)
            }
            else{
                $('#Link_Valence_option1').prop('checked', false);
                $('#Link_Valence_option2').prop('checked', true)
            }
            clicks_link = 0;
        }, DELAY_link);// End Single Click
    } else { //Double Click
        clearTimeout(timer_link);    //prevent single-click action
        target_el.addClass('Selected-link');
        clicks_link = 0;             //after action performed, reset counter
    }//End Double Click

})
.on("dblclick", '.block',function(e){
    e.preventDefault();  //cancel system double-click event
});


$(document).on('mouseup', '#Link_Valence', function (event) {
    event.stopPropagation();
    var target_el = $('.Selected-link').first();
    slider_link_changes(event, target_el, $('#link_slider_choice').val());
    update_link_form_slider(target_el, $('#link_slider_choice').val());

});

$(document).on('mouseup','#link_slider_choice',function (event) {
        // submit change
        var target_el = $('.Selected-link').first();
        slider_link_changes(event, target_el, $(this).val());
        update_link_form_slider(target_el, $(this).val());
        target_el.addClass('Selected-link')
    });

