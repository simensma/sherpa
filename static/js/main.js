$(document).ready(function() {

    $("nav#menus div.language-bar select").change(function() {
        var val = $(this).children("option:selected").val();
        if(val != '') {
            window.location = val;
        }
    });

});
