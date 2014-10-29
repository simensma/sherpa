$(function() {

    var wrapper = $('[data-dnt-container="aktivitet-failed-imports"]');

    wrapper.find('[data-dnt-trigger="helptext"]').click(function() {
        $(this).siblings('[data-dnt-container="helptext"]').slideToggle('fast');
    });

});
