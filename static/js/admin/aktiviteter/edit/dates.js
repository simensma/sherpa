$('[data-dnt-toggle="signup"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).val() === 'none';
    parent.find('[data-dnt-container="signup"]').toggleClass('jq-hide', toggle);
});

$('[data-dnt-toggle="signup-deadline"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).is(':checked');
    parent.find('[data-dnt-container="signup-deadline"]').toggleClass('jq-hide', toggle);
});

$('[data-dnt-toggle="cancel-deadline"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).is(':checked');
    parent.find('[data-dnt-container="cancel-deadline"]').toggleClass('jq-hide', toggle);
});

$('[data-dnt-toggle="turledere"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = !$(this).is(':checked');
    parent.find('[data-dnt-container="turledere"]').toggleClass('jq-hide', toggle);
});

$('[data-dnt-toggle="contact-custom"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).val() !== 'custom';
    parent.find('[data-dnt-container="contact-custom"]').toggleClass('jq-hide', toggle);
});

$('[data-dnt-action="turleder-add"]').on('click', function() {
    var parent = $(this).parents('div.panel-body');
    var table = parent.find('[data-dnt-container="turledere"] table tbody');
    var i = 0; // @TODO how to figure this out?

    // Event handler for selected turleder
    function dateTurlederSelectHandler(e, turleder) {
        console.log('dateTurlederSelectHandler', arguments);

        var btn = $('<button class="btn btn-sm btn-danger">Fjern</button>')
            .data('dntAction', 'turleder-rm')
            .on('click', dateTurlederRemoveHandler);

        var input = $('<input type="hidden" name="dates[' + i + '][turleder][]">')
            .val(turleder.id);

        table.append($('<tr>')
            .append('<td>' + turleder.name + '</td>')
            .append('<td>' + turleder.phone + '<br>' + turleder.email + '</td>')
            .append($('<td>').append(input).append(btn)));
    };

    // Attach modal event handlers and show
    $('[data-dnt-container="turleder-search"]')
        .on('select.dnt.turleder', dateTurlederSelectHandler)
        .one('hide.bs.modal', function() {
            $(this).off('select.dnt.turleder', dateTurlederSelectHandler);
        })
        .modal('show');
});

$('[data-dnt-action="turleder-rm"]').on('click', dateTurlederRemoveHandler);

function dateTurlederRemoveHandler() {
    $(this).parents('tr').remove();
};

