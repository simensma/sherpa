$(window).load(function() {
    var wrapper = $("div.wrapper");
    var list = $("div.article-listing");
    var old_list = $("div.old-article-listing");
    var loader = $("div.article-loader");
    var loading = false;
    var status = 'new';
    list.data('current', list.attr('data-initial-count'));
    old_list.data('current', 0);

    $(window).scroll(function() {
        if(!loading && status != 'complete' && $(window).scrollTop() + $(window).height() > wrapper.offset().top + wrapper.height()) {
            loading = true;
            loadArticles();
        }
    });

    function loadArticles() {
        if(status == 'new') {
            loadNewArticles();
        } else if(status == 'old') {
            loadOldArticles();
        }
    }

    function loadNewArticles() {
        $.ajaxQueue({
            url: '/nyheter/flere/',
            data: { current: list.data('current') }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length == 0) {
                if(old_list.length > 0) {
                    old_list.fadeIn();
                    status = 'old';
                    loadOldArticles();
                } else {
                    loader.fadeOut();
                    status = 'complete';
                }
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
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere nyheter. Prøv å oppdatere siden, og scrolle ned igjen.");
        }).always(function(result) {
            loading = false;
        });
    }

    function loadOldArticles() {
        $.ajaxQueue({
            url: '/nyhetsarkiv/flere/',
            data: { current: old_list.data('current') }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length == 0) {
                loader.fadeOut();
                status = 'complete';
                return;
            }
            old_list.data('current', Number(old_list.data('current')) + result.length);
            for(var i=0; i<result.length; i++) {
                var item = $(result[i]);
                old_list.append(item);
                item.fadeIn();
            }
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere nyheter. Prøv å oppdatere siden, og scrolle ned igjen.");
        }).always(function(result) {
            loading = false;
        });
    }

});
