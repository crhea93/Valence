var DELAY = 500, clicks = 0, timer=null;
$(document).on("click", '.block',function(e){

    e.preventDefault();
    let ct_ = this.id.split("_")[1];
    var target_el = $('#block_'+ct_);
    click_element = 'concept';
    if (concept_sel_bool === true){
        console.log('concept select')
        clicks += 1;
        if (clicks === 1) { //Single Click
            // Is the modification section open
            if (target_el.hasClass('Open')){
                $(e.target).select();
                $('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
                $('#Comment_Box').val('')
                $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
            }
            // Concept is closed
            else{
                // clicked on already selected element
               if (target_el.hasClass('Selected')) {
                    target_el.removeClass('Selected');
                    //clicks -= 1;
                    $('#No_Concept_Comment').attr('hidden', false);
                    $('#Comment_Info').attr('hidden', true);
                }
                // Concept isnt yet selected
                else {
                    // Unselect all other concepts
                   $('.Selected').each(function(){
                       $(this).removeClass('Selected')
                   })
                   target_el.addClass('Selected');
                   // Update Comment Box
                   $('#No_Concept_Comment').attr('hidden', true);
                   $('#Comment_Info').attr('hidden', false);
                   $('#Comment_Box').val('')
            $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
                }
            }timer = setTimeout(function () {
                    clicks = 0;             //after action performed, reset counter
                }, DELAY);// End Single Click
        } else { //Double Click
            clearTimeout(timer);    //prevent single-click action
            $('.block.Open').each(function(){ // Close existing blocks
                close_block_func(this);
              });
            $('#block_form_' + ct_).attr('hidden', false); //Set up form changes
            $('#success_block_' + ct_).empty();
            $('#block_'+ct_).addClass('Open');
            $('#title_'+ct_).select();
            $('.slider').slider('option', 'value', $('#shape_'+ct_).attr('value'));
            $('#No_Concept_Comment').attr('hidden', true); // Allow for concept comment changes
            $('#Comment_Info').attr('hidden', false);
            $('#Comment_Box').val('')
            $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
            clicks = 0;             //after action performed, reset counter
        }//End Double Click
    } // End Concept Selection for Concept Purposes
    else if (line_sel_bool === true){
            target_el.addClass('Selected');
            if ($('.Selected').length === 1){
                /*$('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
                $('#Comment_Box').text($('#block_'+ct_+' > i').attr('title'));*/
            }
            if ($('.Selected').length === 2) {
                $('.Selected-link').each(function(){
                    $(this).removeClass('Selected-link')
                    $(this).children().each(function(){
                        $(this).removeClass('Selected-arrow')
                    })
                });
                create_link();
            }
        /*}*/
    } // End Concept Selection for Lines
    else if (cursor_bool === true){
        if (target_el.hasClass('Selected')) {
                // clicked on already selected element
                target_el.removeClass('Selected');
                $('#No_Concept_Comment').attr('hidden', false);
                $('#Comment_Info').attr('hidden', true);
        } else {
            $('.Selected').each(function(){
                $(this).removeClass('Selected')
            })
            target_el.addClass('Selected');
            // Update Comment Box
            $('#No_Concept_Comment').attr('hidden', true);
            $('#Comment_Info').attr('hidden', false);
            $('#Comment_Box').val('')
            $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
            console.log($('#block_'+ct_+'>span'))
        }
    } // End Concept Selection for Lines
})
.on("dblclick", '.block',function(e){
    e.preventDefault();  //cancel system double-click event
});