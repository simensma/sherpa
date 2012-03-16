$(document).ready(function() {

    $("form#household div.household").hide();
    $("form#household input[name='household']").click(function() {
        if($(this).prop('checked')) {
            $("form#household div.household").show();
        } else {
            $("form#household div.household").hide();
        }
    });

});
