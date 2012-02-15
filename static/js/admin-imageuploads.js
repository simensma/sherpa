$(document).ready(function() {

    $("#image-uploader form").ajaxForm({
        beforeSubmit: function() {
            $("div.well").hide();
            $("input[type='submit']").prop('disabled', true);
        },
        complete: function(response) {
            $(document.body).html(response.responseText);
        }
    });

});
