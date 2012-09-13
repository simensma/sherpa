$(document).ready(function() {
    $("form#gift").hide();
    $("div.gift-choice").click(function() {
        $("div.gift-choice").removeClass('active');
        $(this).addClass('active');
        $("form#gift").show();
    });
});
