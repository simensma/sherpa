$(document).ready(function() {

    $("form#registration input[name='zipcode']").keyup(function() {
        if($(this).val().match(/^\d{4}$/)) {
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#registration input[name='city']").val(result);
            }).fail(function(result) {
                $("form#registration input[name='city']").val("Ukjent postnummer");
            });
        } else {
            $("form#registration input[name='city']").val("");
        }
    });

});
