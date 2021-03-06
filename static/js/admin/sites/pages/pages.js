/* Editing a page (not its contents) */

$(function() {

    /* New page dialog - define slug based on title */

    var validUrl = false;

    var newPage = $("div.new-page");

    $("a.new-page").click(function() {
        newPage.modal({
            maskMessage: 'Oppretter siden...'
        });
    });

    // Enable select2 for setting parent
    newPage.find("select[name='parent_id']").select2();

    newPage.find("img.loader").hide();
    newPage.find("span.valid").hide();
    newPage.find("span.invalid").hide();
    newPage.find("input[name='title']").keyup(function() {
        slugifiedTitle = $(this).val().replace(/[^-_a-z0-9\s]+/gi, '')
                                 .replace(/\s+/g, "-")
                                 .toLowerCase();
        newPage.find('input[name="slug"]').val(slugifiedTitle).trigger('input'); // Trigger input event on slug field
    });

    newPage.find('input[name="slug"]').on('input', function (e) {
        lookupVal = $(this).val();
        initiateLookup();
        clearTimeout(lookupTimer);
        lookupTimer = setTimeout(performLookup, KEY_LOOKUP_DELAY);
    });

    var slugifiedTitle;
    var lookupTimer;
    var lookupVal;
    var KEY_LOOKUP_DELAY = 1000;

    function initiateLookup() {
        newPage.find('.slug span.valid').hide();
        newPage.find('.slug span.invalid').hide();
        newPage.find('img.loader').show();
    }

    function performLookup() {
        // Check dynamically that the slug is unique
        $.ajaxQueue({
            url: newPage.attr('data-check-slug-url'),
            data: 'slug=' + encodeURIComponent(lookupVal)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.valid) {
                validUrl = true;
                newPage.find("span.valid").show();
            } else {
                validUrl = false;
                newPage.find("span.invalid").show();
            }
        }).fail(function(result) {
            // Todo
        }).always(function() {
            newPage.find("img.loader").hide();
        });
    }

    newPage.find('button[data-dnt-action="create-page"]').click(function() {
        if(!validUrl) {
            alert("URLen du valgte er allerede i bruk av en annen side! Vennligst velg en annen URL.");
            return;
        }
        if(newPage.find("input[name='title']").val().length === 0) {
            alert("Du må skrive inn en tittel på siden før du oppretter den!");
            return;
        }
        newPage.find("input[name='template']").val(newPage.find('.template-select .active').attr('data-template'));

        newPage.find("form").submit();

        var $modal = $(this).parents('.modal').first();
        $modal.modal('mask');

    });

    newPage.find('.template-select .template-item').click(function (e) {
        newPage.find('.template-select .template-item.active.selected').removeClass('active selected');
        $(this).addClass('active selected');
    });

    /* Sortable tree */

    $treeContainer = $('div.pages.tree');

    // Collapse all
    $treeContainer.find('.header .disclose .collapse').on('click', function (e) {
        $(this).parents('.disclose').first().addClass('expand-all').removeClass('collapse-all');
        $treeSortable.find('li ol li.has-children').each(function () {
            $(this).addClass('mjs-nestedSortable-collapsed').removeClass('mjs-nestedSortable-expanded');
        });
    });

    // Expand all
    $treeContainer.find('.header .disclose .expand').on('click', function (e) {
        $(this).parents('.disclose').first().addClass('collapse-all').removeClass('expand-all');
        $treeSortable.find('li ol li.has-children').each(function () {
            $(this).addClass('mjs-nestedSortable-expanded').removeClass('mjs-nestedSortable-collapsed');
        });
    });

    $treeSortable = $treeContainer.find('ol.sortable');

    $treeSortable.find('li ol').each(function () {
        $(this).parents().first().addClass('has-children');
    });

    $treeSortable.nestedSortable({
        handle: 'div.handle',
        items: 'li',
        toleranceElement: '> div',
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        disabledClass: 'mjs-nestedSortable-disabled',
        expandOnHover: 700,
        isTree: true,
        protectRoot: true,

        relocate: function (e) {
            var mpttArray = $('ol.sortable').nestedSortable('toArray', {startDepthCount: 0});

            // First item is just... Some kind of wrapper.
            // Remove it and -- all left, right & depth values.
            mpttArray.shift();
            for (var i = 0; i < mpttArray.length; i++) {
                mpttArray[i]['depth']--;
                mpttArray[i]['left']--;
                mpttArray[i]['right']--;
            }

            var url = $(this).attr('data-reorder-url');
            var data = {mptt: mpttArray};

            $.ajax({
                url: url,
                data: data,
                dataType: 'json',
                method: 'POST',
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error(jqXHR, textStatus, errorThrown);
                }
            });

            $treeContainer.find('li:not(.has-children)').each(function () {
                if ($(this).find('ol').length) {
                    $(this).addClass('has-children');
                } else {
                    $(this).removeClass('has-children');
                }
            });

        }

    });

    $('.node-wrapper .disclose').on('click', function() {
        var $li = $(this).closest('li');
        var isExpanded = $li.hasClass('mjs-nestedSortable-expanded');
        if (isExpanded) {
            $li.addClass('mjs-nestedSortable-collapsed').removeClass('mjs-nestedSortable-expanded');
        } else {
            $li.addClass('mjs-nestedSortable-expanded').removeClass('mjs-nestedSortable-collapsed');
        }
    });


    /* Delete page from list view */

    $(document).on('click', '.node-wrapper .actions .delete a', function (e) {

        var modalOptions = {};

        var $li = $(this).parents('li').first();
        modalOptions.hasChildren = !!$li.find('ol').length;
        modalOptions.deleteUrl = $(this).data('dnt-delete-url');
        modalOptions.title = $li.find('.title span').first().text();

        Turistforeningen.setupDeletePageModal(modalOptions);

    });

    /* Init tags tooltip */
    $treeContainer.find('.meta .tags').tooltip();

});
