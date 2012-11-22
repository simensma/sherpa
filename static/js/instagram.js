$(document).ready(function() {

    var loading = false;
    var end = false;
    var wrapper = $("div.instagram-wrapper");
    var loader = wrapper.find("div.loader");
    var ender = wrapper.find("div.ender");

    $(window).scroll(function() {
        if(!loading && !end && $(window).scrollTop() + $(window).height() > loader.offset().top) {
            loading = true;
            $.ajaxQueue({
                url: '/instagram/flere/'
            }).done(function(result) {
                result = JSON.parse(result);
                $(result.content).addClass('hide').insertAfter($("div.instagram").last()).fadeIn();
                if(result.meta.end) {
                    end = true;
                    loader.hide();
                    ender.show();
                }
            }).fail(function(result) {
                alert("Beklager, det oppstod en feil når vi forsøkte å laste flere instagrambilder. Prøv å oppdatere siden, og scrolle ned igjen.");
            }).always(function(result) {
                loading = false;
            });
        }
    });

    $(document).on('mouseenter', 'div.instagram div.container', function() {
        $(this).find('div.hover-content').fadeIn(200);
    });

    $(document).on('mouseleave', 'div.instagram div.container', function() {
        $(this).find('div.hover-content').fadeOut(200);
    });

    $(document).on('click', 'div.instagram div.container', function() {
        window.location = $(this).attr('data-href');
    });

});
