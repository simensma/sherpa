/* Membershipservice */

$(document).ready(function() {
    $("dl dd").hide();
    $("dl dt").click(function() {
        $(this).next().toggle();
    });
});
