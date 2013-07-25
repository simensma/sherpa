(function(InfiniteScroller, $, undefined) {

    // Options
    var url;
    var ajaxData = function() { return {}; };
    var trigger;
    var triggerType;
    var container;
    var loader;
    var handlers = { // default ajax handlers
        done: function(result) {
            result = $(result.trim());
            if(result.length === 0) {
                if(loader !== undefined) {
                    loader.fadeOut();
                }
                complete = true;
                return;
            }
            container.append(result);
        }, fail: function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere elementer. Prøv å oppdatere siden, og scrolle ned igjen.");
        }, always: function(result) {
            loading = false;
            if(loader !== undefined) {
                loader.fadeOut();
            }
            if(triggerType === 'button') {
                trigger.show();
            }
        }
    };

    var loading = false;
    var complete = false;
    var windowLoaded = false;

    $(window).load(function() {
        windowLoaded = true;
    });

    InfiniteScroller.enable = function(opts) {
        url = opts.url;
        if(opts.ajaxData !== undefined) {
            ajaxData = opts.ajaxData;
        }
        trigger = opts.trigger;
        triggerType = opts.triggerType;
        container = opts.container;
        loader = opts.loader;
        if(opts.handlers !== undefined) {
            handlers = opts.handlers;
        }

        if(triggerType === 'scroll') {
            // The enable function could be called before or after window load, so make sure the scroll
            // event isn't added before it's loaded (for element height calculations)
            if(windowLoaded) {
                addScrollEvent();
            } else {
                $(window).load(addScrollEvent);
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
        } else if(triggerType === 'button') {
            trigger.on('click.infinite-scroller', load);
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
        if(loader !== undefined) {
            loader.show();
        }
        if(triggerType === 'button') {
            trigger.hide();
        }
        $.ajaxQueue({
            url: url,
            data: ajaxData()
        }).done(handlers.done).fail(handlers.fail).always(handlers.always);
    }

}(window.InfiniteScroller = window.InfiniteScroller || {}, jQuery ));
