$(window).load(function() {
    var list = $("div.article-listing");
    var loader = list.find("div.article-loader");
    var loading = false;
    var complete = false;
    setScrollPoint();
    list.data('current', list.attr('data-initial-count'));

    $(window).scroll(function() {
        if(!loading && !complete && $(window).scrollTop() + $(window).height() > list.data('scrollpoint')) {
            loadArticles();
        }
    });

    function setScrollPoint() {
        var scrollpoint = list.offset().top + list.height();
        list.data('scrollpoint', scrollpoint);
    }

    function loadArticles() {
        loading = true;
        $.ajaxQueue({
            url: '/nyheter/flere/',
            data: 'current=' + encodeURIComponent(list.data('current'))
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length == 0) {
                loader.fadeOut();
                complete = true;
                return;
            }
            list.data('current', Number(list.data('current')) + result.length);

            // TODO handle end of list
            var first;
            for(var i=0; i<result.length; i++) {
                if(i % 2 == 0) {
                    first = $('<div class="row-fluid">' + result[i] + '</div>');
                } else {
                    first.append(result[i]).addClass('hide');
                    list.append(first);
                    first.fadeIn();
                }
            }
            loader.detach().appendTo(list);
        }).fail(function(result) {
            alert("fail");
        }).always(function(result) {
            setScrollPoint();
            loading = false;
        });
    }

});
