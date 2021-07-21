$(document).on("mousedown", "#CAM_items",function(event) {
      // IF USER CLICKS ON CAM WHITESPACE -- ALL SELECTED ITEMS BECOME UNSELECTED
      pageX_ = event.pageX;
      pageY_ = event.pageY;
      event.preventDefault();
      var CAM = this;
      click_element = 'CAM';
      //Close any existing blocks by submitting them
      timer = setTimeout(function(e) {
      if ((cursor_bool === true || line_sel_bool === true || concept_sel_bool === true) && event.target === CAM) {
          $('#No_Concept_Comment').attr('hidden', false);
             $('#Comment_Info').attr('hidden', true);
          $('.Selected').each(function(){
              $(this).removeClass('Selected')
          });
          $('.Selected-link').each(function(){
              $(this).removeClass('Selected-link');
              $(this).children().each(function(){
                $(this).removeClass('Selected-arrow')
            })
              $('#Link_Info').attr('hidden',true);
              $('#No_Link_Info').attr('hidden',false)
          });
      } // END CLOSE ALL IF CLICK ON WHITESPACE
      // If concept object is selected
      if ((concept_sel_bool === true) && event.target === CAM){
          if ($('.block.Open').length !== 0){
              $('.block.Open').each(function(){
                close_block_func(this);
              });
          }
          else{
              $('#No_Concept_Comment').attr('hidden', false);
              $('#Comment_Info').attr('hidden', true);
              clearTimeout(timer);
              prevent = true;
              place_ret = block_placement(event, $("#CAM_items"), -100-shift_left_total, -50-shift_top_total, concept_ct, 1/currentZoom);
              concept_ct = place_ret[0];X = place_ret[1]; Y = place_ret[2];
              $('.Selected').each(function(){
                    $(this).removeClass("Selected");
                    $(this).removeClass("FirstSelected");
                    $(this).removeClass("SecondSelected");
                });
              $("#block_"+concept_ct).addClass('Selected Open');
          }
      }
      prevent = false;
    }, delay);
});