$(document).ready(function() {

    var overview = $("div.enrollment-overview");

    overview.find("div.enrollment").each(function() {

        var header = $(this).find("div.header");
        var body = $(this).find("div.body");

        header.click(function() {
            header.toggleClass('open');
            header.toggleClass('closed');
            body.slideToggle();
        });

    });

});
