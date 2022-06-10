var DELAY = 500, clicks = 0, timer=null;
$(document).on("click", '.block', function(e){
    e.preventDefault();
    let ct_ = this.id.split("_")[1];
    var target_el = $('#block_'+ct_);
    click_element = 'concept';
    if (concept_sel_bool === true){
        console.log('concept select')
        console.log(parseInt($('#block_'+ct_).css('font-size')))
        clicks += 1;
        if (clicks === 1) { //Single Click
            // Is the modification section open
            if (target_el.hasClass('Open')){
                $(e.target).select();
                $('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
                $('#Comment_Box').val('')
                $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
                $('#NewTextScale').val(parseInt($('#block_'+ct_+' .success_blk').css('font-size')))
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
                   $('#NewTextScale').val(parseInt($('#block_'+ct_+' .success_blk').css('font-size')))
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
            $('#NewTextScale').val(parseInt($('#block_'+ct_+' .success_blk').css('font-size')))
            clicks = 0;             //after action performed, reset counter
        }//End Double Click
    } // End Concept Selection for Concept Purposes
    else if (line_sel_bool === true){
            target_el.addClass('Selected');
            if ($('.Selected').length === 1){
                target_el.addClass('FirstSelected')
                /*$('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
                $('#Comment_Box').text($('#block_'+ct_+' > i').attr('title'));*/
            }
            if ($('.Selected').length === 2) {
                target_el.addClass('SecondSelected')
                $('.Selected-link').each(function(){
                    $(this).removeClass('Selected-link')
                    $(this).children().each(function(){
                        $(this).removeClass('Selected-arrow')
                    })
                });

                // Identify first and last block selected
                var start_block_id = $('.FirstSelected').attr("id").split("_")[1];
                var end_block_id = $('.SecondSelected').attr("id").split("_")[1];

                // Create link only if there's no other link in that direction
                if ($('div[data-start_id|='+start_block_id+']div[data-end_id|='+end_block_id+'],div[data-start_id|='+start_block_id+']div[data-end_id|='+end_block_id+']').length < 1) {
                    create_link();
                    console.log('Created the link: start:'+start_block_id+', end:'+end_block_id)
                }
                else {
                    console.log('Did not create the link, this concept combination already has a link start:'+start_block_id+', end:'+end_block_id)
                }
            // Removing these 'order of selction' classes (used as tags)
            $('div').removeClass("FirstSelected");
            $('div').removeClass("SecondSelected");
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
            console.log($('#block_'+ct_).css('font-size'))
            $('#No_Concept_Comment').attr('hidden', true);
            $('#Comment_Info').attr('hidden', false);
            $('#Comment_Box').val('')
            $('#Comment_Box').val($('#block_'+ct_+' > span').attr('title'));
            $('#NewTextScale').val(parseInt($('#block_'+ct_+' .success_blk').css('font-size')))
        }
    } // End Concept Selection for Lines
})
//.on("dblclick", '.block',function(e){
//    e.preventDefault();  //cancel system double-click event
//});