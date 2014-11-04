$(function() {
    var aktivitet = $('[data-dnt-container="aktivitet"]');

    aktivitet.find('[data-dnt-trigger="alternative-dates"]').click(function() {
        $(this).siblings('[data-dnt-container="alternative-dates"]').show();
        $(this).remove();
    });
});
