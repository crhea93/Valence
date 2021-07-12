$(window).on("beforeunload", function() {
    unload_save()
})
window.setInterval(function(){
    html2canvas(document.querySelector('#CAM_items')).then(function(canvas) {
        /* var dataImage = canvas.toDataURL("image/png");
        $.ajax({
                async:false,
                url: "{% url 'image_CAM' %}",
                type: "POST",
                data: {
                    'csrfmiddlewaretoken': '{{ csrf_token }}',
                    'html_to_convert': dataImage,
                },
        })//end ajax*/
    });
}, 10000)