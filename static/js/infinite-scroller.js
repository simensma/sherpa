(function(InfiniteScroller, $, undefined) {

    var container;
    var loader;
    var loading = false;
    var complete = false;
    var windowLoaded = false;

    $(window).load(function() {
        windowLoaded = true;
    });

    InfiniteScroller.enable = function(opts) {
        container = opts.container;
        loader = opts.loader;
        container.data('infinite-scroller-bulk', 1);

        // The enable function could be called before or after window load, so make sure the scroll
        // event isn't added before it's loaded (for element height calculations)
        if(windowLoaded) {
            addScrollEvent();
        } else {
            $(window).load(addScrollEvent);
        }

        function addScrollEvent() {
            $(window).on('scroll.infinite-scroller', function() {
                var scrollLimit = container.offset().top + container.height();
                if(!loading && !complete && $(window).scrollTop() + $(window).height() > scrollLimit) {
                    loading = true;
                    load();
                }
            });
        }

    };

    InfiniteScroller.disable = function(opts) {
        $(window).off('scroll.infinite-scroller');
    };

    function load() {
        $.ajaxQueue({
            url: container.attr('data-infinite-scroll-url'),
            data: { bulk: container.data('infinite-scroller-bulk') }
        }).done(function(result) {
            result = $(result.trim());
            if(result.length === 0) {
                loader.fadeOut();
                complete = true;
                return;
            }
            container.data('infinite-scroller-bulk', Number(container.data('infinite-scroller-bulk')) + 1);
            container.append(result);
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere elementer. Prøv å oppdatere siden, og scrolle ned igjen.");
        }).always(function(result) {
            loading = false;
        });
    }

}(window.InfiniteScroller = window.InfiniteScroller || {}, jQuery ));
