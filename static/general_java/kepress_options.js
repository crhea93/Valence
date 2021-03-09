$(document).on("keyup", '.block', function(event){
        let ct__ = 0
        if ($(this).attr('data-title') && ct__ === 0){
            if (event.keyCode === 13) {
                 let ct = this.id.split("_")[1];
                 let btn = $("#form_cam_block_button_mod");
                 btn.attr('data-title',ct);
                 btn.click();
                $('#block_form_' + ct).attr('hidden', true);
                $('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
            }
        }
        else{
            if (event.keyCode === 13 && ct__ === 0) {
                let ct = this.id.split("_")[1];
                let btn = $("#form_cam_block_button");
                btn.attr('data-title', ct);
                btn.click();
                $('#block_form_' + ct).attr('hidden', true);
                $('#No_Concept_Comment').attr('hidden', true);
                $('#Comment_Info').attr('hidden', false);
            }
        }

        if (event.keyCode === 46 && console.log($('#Comment_Info')[0].hasAttribute('hidden')) === true) {
            blk_delete(this)
        }
})