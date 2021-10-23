$(document).on('mouseclick', "#UndoAction",function(event) {
    // Ajax call to undo
    $.ajax({
        async: false,
        type: "POST",
        url: "{% url 'undo_action' %}",
        data: {
            'csrfmiddlewaretoken': '{{ csrf_token }}',
        },
        success: function (data) {
            location.reload()  // Reload page
        },
        error: function () {
            console.log("Error")
        }
    })//end ajax
})