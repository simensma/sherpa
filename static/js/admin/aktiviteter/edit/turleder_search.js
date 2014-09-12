$('[data-dnt-container="turleder-search"]').on('show', function() {
    $(this).find('form input').val('');
    $(this).find('table').addClass('jq-hide');
    $(this).find('table tbody tr').remove();
});

$('[data-dnt-container="turleder-search"] form').on('submit', function(e) {
    e.preventDefault();

    var container = $(this).parents('[data-dnt-container="turleder-search"]');
    var table = container.find('table');
    var tbody = table.find('tbody');

    turlederSearchLoading();

    $.ajaxQueue({
        url: $(this).prop('action').replace(/^https?:\/\/[^\/]+/, ''),
        data: { q: $(this).find('input').val() }
    }).done(function(result) {
        result = JSON.parse(result);

        var rows = $(result.results);
        rows.find('button').on('click', turlederSearchRowButtonClickHandler);

        // check progress bar before showing results
        var bar = container.find('.progress-bar');
        if (bar.attr('aria-valuenow') === bar.attr('aria-valuemax')) {
            tbody.html(rows);
            turlederSearchEnable();
        } else {
            bar.one('finished', function() {
                tbody.html(rows);
                turlederSearchEnable();
            }.bind(this));
        }
    }.bind(this));
});

function turlederSearchLoading() {
    var container = $('[data-dnt-container="turleder-search"]');
    container.find('form input').prop('disabled', true);
    container.find('form button').button('loading');

    var bar = $('<div class="progress-bar" style="width: 0%">');
    bar.attr('aria-valuenow', 0);
    bar.attr('aria-valuemin', 0);
    bar.attr('aria-valuemax', 100);

    var progress = $('<div class="progress progress-striped active">').append(bar);
    container.find('table tbody').html($('<td colspan="6">').append(progress));
    container.find('table').removeClass('jq-hide');

    var i = 0;
    var j = setInterval(function() {
        bar.css('width', ++i + '%');
        bar.attr('aria-valuenow', i);

        if (i === 100) {
            clearInterval(j);
            bar.trigger('finished');
        }
    }, 200);
};

function turlederSearchEnable() {
    var container = $('[data-dnt-container="turleder-search"]');
    container.find('form input').prop('disabled', false);
    container.find('form button').button('reset');
};

function turlederSearchRowButtonClickHandler() {
    data = {
        id: $(this).data('dntUserId'),
        name: $(this).data('dntUserName'),
        phone: $(this).data('dntUserPhone'),
        email: $(this).data('dntUserEmail')
    }
    $(this).parents('[data-dnt-container="turleder-search"]')
        .trigger('dnt.turleder.selected', [data]);
    $(this).button('loading');
};

