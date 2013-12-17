$(document).ready(function() {
    var aktivitet = $("div.aktivitet");

    aktivitet.find("a.show-alternative-dates").click(function() {
        var alternatives = $(this).siblings("div.alternatives");
        $(this).remove();
        alternatives.slideDown();
    });
});
