$(document).on("keyup", '.block', function(event){
        console.log(this.title)
        let ct__ = 0
        if (this.title && ct__ === 0){
            if (event.keyCode === 13) {
                 let ct = this.id.split("_")[1]
                 let btn = $("#form_cam_block_button_mod")
                 btn.attr('title',ct)
                 btn.click();
                $('#block_form_' + ct).attr('hidden', true);
                ct__ += 1
            }
        }
        else{
            if (event.keyCode === 13 && ct__ === 0) {
                let ct = this.id.split("_")[1]
                let btn = $("#form_cam_block_button")
                btn.attr('title', ct)
                btn.click();
                $('#block_form_' + ct).attr('hidden', true)
                ct__ += 1
            }
        }
        if (event.keyCode === 46) {
            blk_delete(this)
        }
})