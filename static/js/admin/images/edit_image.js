$(document).ready(function() {

    /* Tags */

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

    $("form.update-image").submit(function() {
        $("input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
    });

    $("form.update-image input[name='photographer']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/fotograf/',
                data: 'name=' + encodeURIComponent(query)
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

});
