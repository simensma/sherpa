$(document).ready(function() {

    var wrapper = $("div.wrapper");
    var list = wrapper.find("div.article-listing");
    var old_list = wrapper.find("div.old-article-listing");
    var loader = wrapper.find("div.infinite-loader");
    var loader_button = loader.find("button");
    var loading = loader.find("div.loading");
    list.data('current', list.attr('data-initial-count'));
    old_list.data('current', 0);

    InfiniteScroller.enable({
        url: list.attr('data-url'),
        ajaxData: function() {
            return { current: list.data('current') };
        },
        triggerType: 'button',
        trigger: loader_button,
        loader: loading,
        handlers: {
            done: function(result) {
                result = JSON.parse(result);
                if(result.length === 0) {
                    old_list.fadeIn();
                    InfiniteScroller.disable();
                    enableOldArticles();
                    return;
                }
                list.data('current', Number(list.data('current')) + result.length);

                var first;
                for(var i=0; i<result.length; i++) {
                    if(i % 2 === 0) {
                        first = $('<div class="row-fluid">' + result[i] + '</div>');
                    } else {
                        first.append(result[i]).addClass('hide');
                        list.append(first);
                        first.fadeIn();
                    }
                }
            }, fail: function(result) {
                alert("Beklager, det oppstod en feil når vi forsøkte å laste flere nyheter. Prøv å oppdatere siden, og scrolle ned igjen.");
            }, always: function(result) {
                loader_button.show();
                loading.hide();
            }
        }
    });

    function enableOldArticles() {
        InfiniteScroller.enable({
            url: old_list.attr('data-url'),
            ajaxData: function() {
                return { current: list.data('current') };
            },
            triggerType: 'button',
            trigger: loader_button,
            loader: loading,
            handlers: {
                done: function(result) {
                    result = JSON.parse(result);
                    if(result.length === 0) {
                        loader.fadeOut();
                        InfiniteScroller.disable();
                        return;
                    }
                    old_list.data('current', Number(old_list.data('current')) + result.length);
                    for(var i=0; i<result.length; i++) {
                        var item = $(result[i]);
                        old_list.append(item);
                        item.fadeIn();
                    }
                }, fail: function(result) {
                    alert("Beklager, det oppstod en feil når vi forsøkte å laste flere nyheter. Prøv å oppdatere siden, og scrolle ned igjen.");
                }, always: function(result) {
                    loader_button.show();
                    loading.hide();
                }
            }
        });

        loader_button.click();
    }

});
