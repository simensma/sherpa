$(window).load(function() {
    // Don't enable editing until the entire window is loaded
    enableEditing();
});

/* Common for avanced- and article-editor */
$(document).ready(function() {

    $("div.no-save-warning").hide();
    selectableContent($(".editable"));
    setEmpties();

    /* Add widget/text/image */

    var noStructureForContentWarning = "Det er ingen rader/kolonner å sette inn innhold i! " +
        "Gå til 'struktur'-knappen først, og legg til noen rader og kolonner.";
    $("#toolbar button.add-widget").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til widget...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til widget her", $("article .column"), function() {
            // Todo: insert widget
            enableToolbar();
            $("article .insertable").remove();
            refreshSort();
            setEmpties();
        });
    });
    $("#toolbar button.add-image").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til bilde...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til bilde her", $("article .column"), function(event) {
            var image = $('<img class="changeable" src="/static/img/article/placeholder-bottom.png" alt="placeholder">');
            var br = $('<br>');
            var editable = $('<div class="editable">BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></div>');
            var content = $("<div/>").append(image, br, editable);
            function done() {
                selectableContent(editable);
                changeableImages(image);
                if(sortState == 'formatting') {
                    editable.attr('contenteditable', 'true');
                }
                refreshSort();
                setEmpties();
                // We don't want the default overlay to be there when we pick a new picture.
                // It will be disabled when the ajax 'always' callback is called, but that's
                // after this callback is done, so we'll just disable it twice.
                disableOverlay();
                image.click();
            }
            addContent($(event.target), content, 'h', done);
        });
    });
    $("#toolbar button.add-text").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til tekst...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til tekst her", $("article .column"), function(event) {
            var content = $('<div class="editable"><p><br></p></div>');
            function done() {
                selectableContent(content);
                if(sortState == 'formatting') {
                    content.attr('contenteditable', 'true').focus();
                }
                refreshSort();
                setEmpties();
            }
            addContent($(event.target), content, 'h', done);
        });
    });

    /* Remove content */
    $("#toolbar button.remove-content").click(function() {
        function doneRemoving() {
            enableEditing();
            $("article .content").off('hover click');
            enableToolbar();
        }
        disableToolbar('Klikk på innholdet i artikkelen du vil ta bort...', doneRemoving);
        disableEditing();
        $("article .content").hover(function() {
            $(this).addClass('hover-remove');
        }, function() {
            $(this).removeClass('hover-remove');
        }).click(function() {
            var content = $(this);
            $.ajax({
                url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(content.attr('data-id')) + '/',
                type: 'POST'
            }).done(function(result) {
                if(content.siblings().length == 0) {
                    setEmpty(content.parent());
                }
                content.remove();
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                refreshSort();
                doneRemoving();
            });
        });
    });

    // Make toolbar draggable
    $("#toolbar").draggable({
        containment: 'window'
    });
    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');

    /* Toolbar buttons */

    $("#toolbar div.button").mousedown(function() {
        $(this).toggleClass('active');
    }).mouseup(function() {
        $(this).toggleClass('active');
    }).hover(function() {
        $(this).toggleClass('hover');
    });

    $("#toolbar select").change(function() {
        $("select option:selected").each(function() {
            document.execCommand('formatblock', false, $(this).val());
        });
        $("#toolbar select").val("default");
    });
    $("#toolbar button.anchor-add").click(function(event) {
        document.execCommand('createLink', false, $("input.url").val());
    });
    $("#toolbar button.anchor-remove").click(function(event) {
        document.execCommand('unlink');
    });
    $("#toolbar div.button.bold").click(function(event) {
        document.execCommand('bold');
    });
    $("#toolbar div.button.italic").click(function(event) {
        document.execCommand('italic');
    });
    $("#toolbar div.button.underline").click(function(event) {
        document.execCommand('underline');
    });
    $("#toolbar div.button.ol").click(function(event) {
        document.execCommand('insertorderedlist');
    });
    $("#toolbar div.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist');
    });
    $("#toolbar div.button.align-left").click(function(event) {
        document.execCommand('justifyleft');
    });
    $("#toolbar div.button.align-center").click(function(event) {
        document.execCommand('justifycenter');
    });
    $("#toolbar div.button.align-right").click(function(event) {
        document.execCommand('justifyright');
    });
    $("#toolbar div.button.full").click(function(event) {
        document.execCommand('justifyfull');
    });

    /* Structure - add row with columns */
    $("#toolbar button.add-columns").click(function() {
        disableToolbar("Velg hvor i artikkelen du vil legge til en ny rad...", function() {
            $(".insertable").remove();
        });
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
                var order = insertable.prevAll(":not(.insertable)").length;
                $.ajax({
                    url: '/sherpa/cms/kolonner/ny/',
                    type: 'POST',
                    data: "version=" + encodeURIComponent($("article").attr("data-id")) +
                          "&order=" + encodeURIComponent(order) +
                          "&columns=" + encodeURIComponent(JSON.stringify(columns))
                }).done(function(result) {
                    var wrapper = $('<div class="row"></div>');
                    for(var i=0; i<columns.length; i++) {
                        wrapper.append($('<div class="column span' + columns[i].span + ' offset' +
                            columns[i].offset + '"></div>'));
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
                        setEmpty($(this));
                    });
                    wrapper.sortable({disabled: true});
                    refreshSort();
                }).fail(function(result) {
                    // Todo
                }).always(function(result) {
                    $("article .insertable").remove();
                    disableOverlay();
                    enableToolbar();
                });
            }
        });
    });
    // Remove row
    $("#toolbar .tab-pane.structure button.remove-columns").click(function() {
        function doneRemoving() {
            enableEditing();
            enableToolbar();
            $("article .row").off('hover click');
        }
        disableToolbar("Velg raden du vil fjerne...", doneRemoving);
        disableEditing();
        $("article .row").hover(function() {
            $(this).addClass('hover-remove');
        }, function() {
            $(this).removeClass('hover-remove');
        }).click(function() {
            var row = $(this);
            $.ajax({
                url: '/sherpa/cms/rad/slett/' + encodeURIComponent(row.attr('data-id')) + '/',
                type: 'POST'
            }).done(function(result) {
                row.remove();
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                refreshSort();
                doneRemoving();
            });
        });
    });
    // Edit mode - formatting, move vertically/horizontally
    var sortState = 'formatting';
    $("article").sortable({ disabled: true });
    $("article .row").sortable({ disabled: true });
    $("#toolbar .structure button.formatting").button('toggle');
    $("#toolbar .structure button.formatting").click(function() {
        disableSort($("article"));
        disableSort($("article .row"));
        $("article .editable").attr('contenteditable', 'true');
        sortState = 'formatting';
    });
    $("#toolbar .structure button.horizontal").click(function() {
        disableSort($("article"));
        enableSort($("article .row"), 'horizontal');
        $("article .editable").removeAttr('contenteditable');
        sortState = 'horizontal';
    });
    $("#toolbar .structure button.vertical").click(function() {
        enableSort($("article"), 'vertical');
        disableSort($("article .row"));
        $("article .editable").removeAttr('contenteditable');
        sortState = 'vertical';
    });
    function disableSort(el) {
        el.sortable('disable');
        el.children().off('mouseenter');
        el.children().off('mouseleave');
    }
    function enableSort(el, alignment) {
        el.sortable('enable');
        el.children().on('mouseenter', function() {
            $(this).addClass('moveable ' + alignment);
        });
        el.children().on('mouseleave', function() {
            $(this).removeClass('moveable ' + alignment);
        });
    }
    function refreshSort() {
        $("article").sortable('refresh');
        $("article .row").sortable('refresh');
        if(sortState == 'vertical') {
            enableSort($("article"), sortState);
        } else if(sortState == 'horizontal') {
            enableSort($("article .row"), sortState);
        }
    }

    /* Saving document */

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 30) {
            $("#toolbar span.save-text").html("<i class=\"icon-ok\"></i> Artikkelen er nylig lagret.");
        } else if(lastSaveCount < 60) {
            $("#toolbar span.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + lastSaveCount + " sekunder siden.");
        } else {
            $("#toolbar span.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + Math.floor(lastSaveCount / 60) + " minutt" + (lastSaveCount >= 120 ? 'er' : '') + " siden.");
        }

        if(lastSaveCount == 60 * 5) {
            $("div.no-save-warning").show();
        }

        if($("#toolbar .save input.autosave:checked").length == 1) {
            var val = $("#toolbar .save input.autosave-frequency").val();
            if(val.match(/^\d+$/) && lastSaveCount > (val * 60)) {
                $("#toolbar .save button.save").click();
                return;
            }
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    // Warn when autosave-number is invalid
    $("#toolbar .save input.autosave-frequency").keyup(function() {
        if($(this).val().match(/^\d+$/)) {
            $(this).parents(".control-group").removeClass('error');
        } else {
            $(this).siblings("input.autosave").removeAttr('checked');
            $(this).parents(".control-group").addClass('error');
        }
    });

    $("#toolbar .save button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).hide();
        $("div.no-save-warning").hide();
        $("#toolbar span.save-text").text("Lagrer, vennligst vent...");
        enableOverlay();
        disableEditing();
        var rows = [];
        $("article div.row").each(function() {
            var row = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            rows = rows.concat([row]);
        });
        var columns = [];
        $("article div.column").each(function() {
            var column = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            columns = columns.concat([column]);
        });
        var contents = [];
        $("article div.content").each(function() {
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: $(this).html()
            };
            contents = contents.concat([content]);
        });

        $.ajax({
            url: '/sherpa/cms/editor/' + $("article").attr('data-id') + '/',
            type: 'POST',
            data: "rows=" + encodeURIComponent(JSON.stringify(rows)) +
                  "&columns=" + encodeURIComponent(JSON.stringify(columns)) +
                  "&contents=" + encodeURIComponent(JSON.stringify(contents))
        }).done(function(result) {
            lastSaveCount = 0;
        }).fail(function(result) {
            // Todo
            $(document.body).html(result.responseText);
        }).always(function(result) {
            updateSaveCount();
            disableOverlay();
            $("#toolbar button.save").show();
            enableEditing();
        });
    });

});

/* Toggle overlay for the entire site */
function enableOverlay() {
    $("<div class=\"ui-widget-overlay\"></div>").appendTo('body');
    $("<div class=\"overlay-loader\"><h3>Lagrer, vennligst vent...</h3><p><img src=\"/static/img/ajax-loader-large.gif\" alt=\"Lagrer, vennligst vent...\"></p></div>")
      .appendTo('body');
}
function disableOverlay() {
    $(".ui-widget-overlay,.overlay-loader").remove();
}

/* Toggle toolbar usage */
function disableToolbar(displayText, cancelCallback) {
    $("#toolbar .tab-pane *").hide();
    var btn = $('<button class="btn cancel">Avbryt</button>');
    btn.click(enableToolbar);
    btn.click(cancelCallback);
    $("#toolbar .tab-pane").append('<p class="cancel">' + displayText + '</p>', btn);
}
function enableToolbar() {
    $("#toolbar .tab-pane .cancel").remove();
    $("#toolbar .tab-pane *").show();
}

/* Toggle editing of the actual content */
function disableEditing() {
    $("article .editable").removeAttr('contenteditable');
    $("article img.changeable").off('click');
}
function enableEditing() {
    $("article .editable").attr('contenteditable', 'true');
    changeableImages($("article img.changeable"));
}

/* Adds event listeners to images for changing the image */
function changeableImages(images) {
    images.hover(function() {
        $(this).addClass('hover');
    }, function() {
        $(this).removeClass('hover');
    }).click(function() {
        $(this).removeClass('hover');
        var src = prompt("URL?");
        if(src !== null && src !== undefined) {
            $(this).attr('src', src);
        }
    });
}

/* Adds event listeners to selected content for highlighting it */
function selectableContent(content) {
    content.click(function() {
        $(this).addClass('selected');
    }).focusout(function() {
        $(this).removeClass('selected');
    });
}

/* Divs for inserting widgets/images/text */
function insertables(text, container, click) {
    var well = $('<div class="insertable well">' + text + '</div>');
    well.click(click);
    var children = container.children();
    container.prepend(well);
    children.each(function() {
        well = well.clone(true);
        $(this).after(well);
    });
}

/* Add content-objects to some column */
function addContent(insertable, content, type, done) {
    enableOverlay();
    var order = insertable.prevAll(":not(.insertable)").length;
    $.ajax({
        url: '/sherpa/cms/innhold/ny/',
        type: 'POST',
        data: "column=" + encodeURIComponent(insertable.parent(".column").attr("data-id")) +
              "&order=" + encodeURIComponent(order) +
              "&content=" + encodeURIComponent($("<div/>").append(content).html()) +
              "&type=" + encodeURIComponent(type)
    }).done([function(result) {
        var wrapper = $('<div class="content" data-id="' + result + '"></div>').append(content);
        var prev = insertable.prev();
        if(prev.length == 0) {
            insertable.parent().prepend(wrapper);
        } else {
            prev.after(wrapper);
        }
    }, done]).fail(function(result) {
        // Todo
    }).always(function(result) {
        enableToolbar();
        $("article .insertable").remove();
        disableOverlay();
    });
}

/* Show/remove placeholder text for empty columns */
function setEmpty(column) {
    column.append('<div class="empty well">Tom kolonne</div>');
}
function setEmpties() {
    $("article .column").each(function() {
        if($(this).children(":not(.insertable)").length == 0) {
            setEmpty($(this));
        }
    });
}
function removeEmpties() {
    $("article .column").children("div.empty.well").remove();
}
