//---------CHECKBOX--------------//
function checkbox_changes(checkbox_elem,block_,ct) {
        if (checkbox_elem.is(':checked')) {
            block_.removeClass();
            block_.addClass('block card draggable ui-widget-content rectangle Open');
            block_.css('background', 'rgba(255, 255, 204, 1)');
            block_.css('border-color', 'yellow');
            document.getElementById("shape_" + ct).disabled = false;
        }
        else if (!checkbox_elem.is(':checked')) {
            block_.removeClass();
            block_.addClass('block card draggable ui-widget-content hexagonAmb Open');
            //block_.addClass('block card draggable ui-widget-content  clip-each border-style-thin-amb fill-hex-amb');
            block_.css('background', '#D165FF');//rgb(179,16,226,1)');
            block_.css('border-color', '#D165FF');
            //checkbox_elem.prop('checked',true);
            document.getElementById("shape_" + ct).disabled = true;
        }
}