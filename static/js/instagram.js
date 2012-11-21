$(document).ready(function() {

    var loading = false;
    var wrapper = $("div.instagram-wrapper");
    var loader = wrapper.find("div.loader");

    $(window).scroll(function() {
        if(!loading && $(window).scrollTop() + $(window).height() > loader.offset().top) {
            loading = true;
            $.ajaxQueue({
                url: '/instagram/flere/'
            }).done(function(result) {
                $(result).addClass('hide').insertAfter($("div.instagram").last()).fadeIn();
            }).fail(function(result) {
                alert("Beklager, det oppstod en feil når vi forsøkte å laste flere instagrambilder. Prøv å oppdatere siden, og scrolle ned igjen.");
            }).always(function(result) {
                loading = false;
            });
        }
    });

});
