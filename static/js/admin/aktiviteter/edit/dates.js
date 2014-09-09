var scope = $('div.section.dates');

$.fn.activity_datepicker = function() {
    return $(this).datepicker({
        format: 'dd.mm.yyyy',
        language: 'no',
        autoclose: true,
        weekStart: 1
    });
}

/**
 * Logic for adding a new date to the DOM
 *
 * 1. Clone template
 * 2. Change {{ tmp }} to i
 * 3. Add to panels
 * 4. Open the new panel
 * 5. Init datepickers
 */
scope.find('[data-dnt-add="date"]').on('click', function() {
    var i = $('[data-dnt-container="dates"]').children().length;
    var clone = $('[data-dnt-template="date"] > div').clone(true, true);

    // Change all tmp values in template to correct i for date.
    clone.find('a[href="#date-tmp"]').attr('href', '#date-' + i);
    clone.find('div#date-tmp').attr('id', 'date-' + i);
    clone.find('[name^="dates[tmp]"]').each(function() {
        $(this).attr('name', $(this).attr('name').replace('dates[tmp]', 'dates[' + i + ']'));
    });

    $('[data-dnt-container="dates"]').append(clone);
    // WTF? Why does not $('.collapse').collapse('toggle') work?
    clone.find('[data-toggle="collapse"]').click();

    // It is visible lets rock them dates
    clone.find('div.input-group.date').activity_datepicker();
});

scope.find('[data-dnt-container="dates"] div.input-group.date').activity_datepicker();

scope.find('[data-dnt-update="date-title"]').on('change', function() {
    var parent = $(this).parents('div.panel');

    var start = parent.find('input[name$="[start_date]"]').val() || 'Ingen startdato';
    var end = parent.find('input[name$="[end_date]"]').val() || 'Ingen sluttdato';

    parent.find('[data-dnt-container="date-title"]').html(start + ' - ' + end);
});

scope.find('[data-dnt-toggle="date-signup"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).val() === 'none';
    parent.find('[data-dnt-container="date-signup"]').toggleClass('jq-hide', toggle);
});

scope.find('[data-dnt-toggle="date-signup-deadline"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).is(':checked');
    parent.find('[data-dnt-container="date-signup-deadline"]').toggleClass('jq-hide', toggle);
});

scope.find('[data-dnt-toggle="date-cancel-deadline"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).is(':checked');
    parent.find('[data-dnt-container="date-cancel-deadline"]').toggleClass('jq-hide', toggle);
});

scope.find('[data-dnt-toggle="date-turledere"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = !$(this).is(':checked');
    parent.find('[data-dnt-container="date-turledere"]').toggleClass('jq-hide', toggle);
});

scope.find('[data-dnt-toggle="date-contact-custom"]').on('change', function() {
    var parent = $(this).parents('div.panel-body');
    var toggle = $(this).val() !== 'custom';
    parent.find('[data-dnt-container="date-contact-custom"]').toggleClass('jq-hide', toggle);
});

scope.find('[data-dnt-action="date-turleder-add"]').on('click', function() {
    var parent = $(this).parents('div.panel-body');
    var table = parent.find('[data-dnt-container="date-turledere"] table tbody');
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

scope.find('[data-dnt-action="date-turleder-rm"]').on('click', dateTurlederRemoveHandler);

function dateTurlederRemoveHandler() {
    $(this).parents('tr').remove();
};

