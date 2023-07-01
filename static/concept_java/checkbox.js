//---------CHECKBOX--------------//
function checkbox_changes(checkbox_elem,block_,ct) {
        if (checkbox_elem.is(':checked')) {
            block_.removeClass();
            block_.addClass('block card shadow-none draggable ui-widget-content rectangle Open');
        }
        else if (!checkbox_elem.is(':checked')) {
            block_.removeClass();
            block_.addClass('block card shadow-none draggable ui-widget-content hexagonAmb Open');
        }
}
