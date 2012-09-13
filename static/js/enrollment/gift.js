$(document).ready(function() {
    $("form#gift").hide();
    $("div.gift-choice").click(function() {
        $("div.gift-choice").removeClass('active');
        $(this).addClass('active');
        $("p.type-display span").hide();
        $("p.type-display span." + $(this).attr('data-name')).show();
        $("form#gift").show();
    });
});
