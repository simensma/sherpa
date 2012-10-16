$(document).ready(function() {

    $("table.multiple-metadata button.new, table.multiple-metadata button.keep").click(function(e) {
        e.preventDefault();
        $(this).toggle();
        $(this).siblings("button.keep, button.new").toggle();
        $(this).parents("td").siblings("td.new").toggle();
        $(this).parents("td").siblings("td.keep").toggle();
    });

    var tagger = new Tagger($("input[name='tags']"), function(tag) {
        // New tag added
        var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + tag + '</div>');
        $("div.tag-box").append(tag);
    }, function(tag) {
        // Existing tag
        $("div.tag-box div.tag").each(function() {
            if($(this).text().trim().toLowerCase() == tag.toLowerCase()) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
            }
        });
    });

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    tagger.tags = tags;

    // Add events to the tag remover button
    $(document).on('mouseover', 'div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-hover.png');
    });
    $(document).on('mouseout', 'div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-default.png');
    });
    $(document).on('click', 'div.tag-box div.tag a', function() {
        tagger.removeTag($(this).parent().text().trim());
        $(this).parent().remove();
    });

    $("form.update-images").submit(function() {
        $("input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
        var fields = {
            description: $("table.multiple-metadata tr.description button.new:hidden").length > 0,
            photographer: $("table.multiple-metadata tr.photographer button.new:hidden").length > 0,
            credits: $("table.multiple-metadata tr.credits button.new:hidden").length > 0,
            licence: $("table.multiple-metadata tr.licence button.new:hidden").length > 0
        };
        $("input[name='fields']").val(JSON.stringify(fields));
    });

});
