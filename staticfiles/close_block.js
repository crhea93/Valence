function close_block_func(block_close_elem){
    $(block_close_elem).removeClass('Open'); //No need to keep this open
    console.log(block_close_elem)
    let ct = block_close_elem.id.split("_")[1]; //because id is block_#
    let btn = '' //initialize
    if (block_close_elem.title) {
        console.log('updating block');
        btn = $("#form_cam_block_button_mod") //The block already exists so we are just modifying it
    } else {
        console.log('submitting block');
        btn = $("#form_cam_block_button") //This is the first time the block is sent to the database
    }
    btn.attr('title', ct);
btn.click();
}