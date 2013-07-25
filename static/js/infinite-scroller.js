(function(InfiniteScroller, $, undefined) {

    var container;
    var trigger;
    var triggerType;
    var loader;
    var handlers;
    var loading = false;
    var complete = false;
    var windowLoaded = false;

    $(window).load(function() {
        windowLoaded = true;
    });

    InfiniteScroller.enable = function(opts) {
        container = opts.container;
        trigger = opts.trigger;
        triggerType = opts.triggerType;
        loader = opts.loader;
        if(opts.handlers !== undefined) {
            handlers = opts.handlers;
        } else {
            // Default ajax handlers
            handlers = {
                done: function(result) {
                    result = $(result.trim());
                    if(result.length === 0) {
                        loader.fadeOut();
                        complete = true;
                        return;
                    }
                    container.data('infinite-scroller-bulk', Number(container.data('infinite-scroller-bulk')) + 1);
                    container.append(result);
                }, fail: function(result) {
                    alert("Beklager, det oppstod en feil når vi forsøkte å laste flere elementer. Prøv å oppdatere siden, og scrolle ned igjen.");
                }, always: function(result) {
                    loading = false;
                    loader.fadeOut();
                    if(triggerType === 'button') {
                        trigger.show();
                    }
                }
            };
        }
        container.data('infinite-scroller-bulk', 1);

        if(triggerType === 'scroll') {
            // The enable function could be called before or after window load, so make sure the scroll
            // event isn't added before it's loaded (for element height calculations)
            if(windowLoaded) {
                addScrollEvent();
            } else {
                $(window).load(addScrollEvent);
            }
        } else if(triggerType === 'button') {
            trigger.on('click.infinite-scroller', load);
        }

        function addScrollEvent() {
            $(window).on('scroll.infinite-scroller', function() {
                var scrollLimit = trigger.offset().top + trigger.height();
                if(!loading && !complete && $(window).scrollTop() + $(window).height() > scrollLimit) {
                    loading = true;
                    load();
                }
            });
        }

    };

    InfiniteScroller.disable = function(opts) {
        if(triggerType === 'scroll') {
            $(window).off('scroll.infinite-scroller');
        } else if(triggerType === 'button') {
            trigger.off('click.infinite-scroller');
        }
    };

    function load() {
        loader.show();
        if(triggerType === 'button') {
            trigger.hide();
        }
        $.ajaxQueue({
            url: container.attr('data-infinite-scroll-url'),
            data: { bulk: container.data('infinite-scroller-bulk') }
        }).done(handlers.done).fail(handlers.fail).always(handlers.always);
    }

}(window.InfiniteScroller = window.InfiniteScroller || {}, jQuery ));
