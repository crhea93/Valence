var DELAY = 200, clicks = 0, timer = null;
var ctrl_clicks = 0; //Number of control clicks
$(document).on("click", '.block',function(e){
     let ct_ = this.id.split("_")[1];
    var target_el = $('#block_'+ct_);
    click_element = 'concept'
    if (event.ctrlKey || event.metaKey) { //Control click
        if (target_el.hasClass('Selected')) {
            target_el.removeClass('Selected');
            ctrl_clicks -= 1;
        } else {
            target_el.addClass('Selected');
            ctrl_clicks += 1;
            if (ctrl_clicks === 2){
                //Place line between clicked elements
                create_link();
                ctrl_clicks = 0;
                //link added
            }
            else{
                //Do nothing
            }// End link adding
        }// End adding class
        //Check if two elements are selected

    }//end control click
    else { //if normal click
        clicks++;  //count clicks
        console.log('click: '+clicks);
        if (clicks === 1) { //Single Click
            if (target_el.hasClass('Selected')) {
                //target_el.removeClass('Selected');
                clicks -= 1;
            } else {
                target_el.addClass('Selected');
                if ($('.Selected').length === 2) {
                    create_link();
                    clicks = 0;
                }

            }timer = setTimeout(function () {
                    clicks = 0;             //after action performed, reset counter
                }, DELAY);// End Single Click
        } else { //Double Click
            clearTimeout(timer);    //prevent single-click action
            $('#block_form_' + ct_).attr('hidden', false);
            $('#success_block_' + ct_).empty();
            $('#block_'+ct_).addClass('Open');
            $('#title_'+ct_).select();
            clicks = 0;             //after action performed, reset counter
        }//End Double Click
    }//End normal click

})
.on("dblclick", '.block',function(e){
    e.preventDefault();  //cancel system double-click event
});
