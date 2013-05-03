$(document).ready(function() {

    var end = false;
    var wrapper = $("div.instagram-wrapper");
    var items = wrapper.find("div.items");
    var loader = wrapper.find("div.infinite-loader");
    var loader_button = loader.find("button");
    var loading = loader.find("div.loading");
    var ender = wrapper.find("div.ender");
    var skeleton = wrapper.find("div.instagram-skeleton");
    var iteration = 0;

    loader_button.click(function() {
        loader_button.hide();
        loading.fadeIn();
        $.ajaxQueue({
            url: '/instagram/last/'
        }).done(function(result) {
            result = JSON.parse(result);
            for(var i=0; i<result.items.length; i++) {
                var instagram = $("div.instagram").last();
                if(iteration === 0) {
                    instagram = skeleton.clone();
                    instagram.removeClass('instagram-skeleton hide').addClass('instagram').appendTo(items);
                }
                var item = $(result.items[i]).addClass('hide');
                var children = instagram.children();
                if(iteration < 5) {
                   item.appendTo(children.first());
                } else if(iteration < 6) {
                   item.appendTo(children.slice(1, 2));
                } else if(iteration < 9) {
                   item.appendTo(children.slice(2, 3));
                } else if(iteration < 12) {
                   item.appendTo(children.slice(3, 4));
                } else if(iteration < 17) {
                   item.appendTo(children.slice(4, 5));
                } else {
                   item.appendTo(children.last());
                }
                item.filter(".display").slideDown();
                iteration += 1;
                if(iteration == 18) {
                    iteration = 0;
                }
            }
            if(result.meta.end) {
                end = true;
                loader.hide();
                ender.show();
            }
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere instagrambilder. Prøv igjen, eller oppdater siden ved å trykke på F5.");
        }).always(function(result) {
            loading.hide();
            loader_button.show();
        });
    });

    $(document).on('mouseenter', 'div.instagram div.display', function() {
        $(this).find('div.hover-content').fadeIn(200);
    });

    $(document).on('mouseleave', 'div.instagram div.display', function() {
        $(this).find('div.hover-content').fadeOut(200);
    });

    // Trigger the first load
    loader_button.click();

});
