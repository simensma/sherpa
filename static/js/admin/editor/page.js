$(document).ready(function() {

    /* Automatically remove empty html contents */
    $(document).on('focusout', 'div.html', function() {
        if($(this).text().trim() === "") {
            disableEditing();
            var html = $(this);
            $.ajax({
                url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(html.attr('data-id')) + '/',
                type: 'POST'
            }).done(function(result) {
                if(html.siblings().length == 0) {
                    setEmpty(html.parent());
                }
                html.remove();
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                refreshSort();
                enableEditing();
            });
        }
    });

});
