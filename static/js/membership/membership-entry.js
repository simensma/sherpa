$(document).ready(function() {

    var entry = $("div.membership-entry");
    var entry_box = entry.find("div.entry-box");
    var show_benefits = entry_box.find("p.show-benefits a");
    var benefits = entry_box.find("div.benefits");

    show_benefits.click(function() {
        $(this).parent().hide();
        benefits.slideDown();
    });

});
