$(document).ready(function() {

    // Structure - add row with columns
    $("#toolbar button.cancel-structure").hide().click(function() {
        $("#toolbar button.add-columns").removeAttr('disabled');
        $(this).hide();
        $(".insertable").remove();
    });
    $("#toolbar button.add-columns").click(function() {
        $(this).attr('disabled', true);
        $("#toolbar button.cancel-structure").show();
        insertables("Klikk her for å sette inn en rad", $("article"), function(event) {
            var choice = Number(prompt("0, 1, 2, 3?"));
            if(!isNaN(choice)) {
                var insertable = $(this);
                var columns;
                if(choice == 0) {
                    columns = [{span: 12, offset: 0, order: 0}]
                } else if(choice == 1) {
                    columns = [{span: 6, offset: 0, order: 0},
                               {span: 6, offset: 0, order: 1}]
                } else if(choice == 2) {
                    columns = [{span: 9, offset: 0, order: 0},
                               {span: 3, offset: 0, order: 1}]
                } else if(choice == 3) {
                    columns = [{span: 4, offset: 0, order: 0},
                               {span: 4, offset: 0, order: 1},
                               {span: 4, offset: 0, order: 2}]
                }
                var order;
                if(insertable.prev().length > 0) {
                    order = Number(insertable.prev().attr("data-order")) + 1;
                } else {
                    order = 0;
                }
                $.ajax({
                    url: '/sherpa/cms/kolonner/ny/',
                    type: 'POST',
                    data: "version=" + encodeURIComponent($("article").attr("data-id")) +
                          "&order=" + encodeURIComponent(order) +
                          "&columns=" + encodeURIComponent(JSON.stringify(columns))
                }).done(function(result) {
                    var wrapper = $('<div class="row" data-order="' + order + '"></div>');
                    for(var i=0; i<columns.length; i++) {
                        wrapper.append($('<div class="column span' + columns[i].span + ' offset' +
                            columns[i].offset + '" data-order="' + columns[i].order + '"></div>'));
                    }
                    var prev = insertable.prev();
                    if(prev.length == 0) {
                        insertable.parent().prepend(wrapper);
                    } else {
                        prev.after(wrapper);
                    }
                    var ids = JSON.parse(result);
                    wrapper.attr("data-id", ids[0]);
                    var i = 1;
                    wrapper.children().each(function() {
                        $(this).attr("data-id", ids[i++]);
                    });
                }).fail(function(result) {
                    // Todo
                }).always(function(result) {
                    $("article .insertable").remove();
                    disableOverlay();
                });
            }
        });
    });

    // Edit mode - formatting, move vertically/horizontally
    var rows = $("article");
    var columns = $("article row");
    rows.sortable({ disabled: true });
    columns.sortable({ disabled: true });
    $("#toolbar #tabs input.formatting").click(function() {
        disableSort(rows);
        disableSort(columns);
        $(".cms-content").attr('contenteditable', 'true');
    });
    $("#toolbar #tabs input.vertical").click(function() {
        enableSort(rows, 'vertical');
        disableSort(columns);
        $(".cms-content").attr('contenteditable', 'false');
    });
    $("#toolbar #tabs input.horizontal").click(function() {
        disableSort(rows);
        enableSort(columns, 'horizontal');
        $(".cms-content").attr('contenteditable', 'false');
    });

    function disableSort(element) {
        element.sortable('disable');
        element.children().off('mouseenter');
        element.children().off('mouseleave');
    }

    function enableSort(element, alignment) {
        element.sortable('enable');
        element.children().on('mouseenter', function() {
            $(this).addClass('moveable ' + alignment);
        });
        element.children().on('mouseleave', function() {
            $(this).removeClass('moveable ' + alignment);
        });
    }

    // Allow content editing of content elements
    $(".cms-content").attr('contenteditable', 'true');

    /* Saving document */

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 30) {
            $("#toolbar p.save-text").html("<i class=\"icon-ok\"></i> Artikkelen er nylig lagret.");
        } else if(lastSaveCount < 120) {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + lastSaveCount + " sekunder siden.");
        } else {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + Math.floor(lastSaveCount / 60) + " minutter siden.");
        }

        if(lastSaveCount == 60 * 5) {
            $("div.no-save-warning").show();
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    $("#toolbar button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).hide();
        $("div.no-save-warning").hide();
        $("#toolbar p.save-text").text("Lagrer, vennligst vent...");
        enableOverlay();
        $(".cms-content").each(function(c) {
            $.ajax({
                url: '/sherpa/cms/innhold/oppdater/' + $(this).attr('data-id') + '/',
                type: 'POST',
                data: "content=" + encodeURIComponent($(this).html())
            }).done(function(result) {
                lastSaveCount = 0;
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                updateSaveCount();
                disableOverlay();
                $("#toolbar button.save").show();
            });
        });
    });

});
