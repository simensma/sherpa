$(document).ready(function() {

    var user = $("div.admin-user-show");
    var nav = user.find("ul.main-nav");
    var tabs = user.find("div.main-nav-tabs");

    tabs.find("div.tab-pane").each(function() {
        var id = $(this).attr('id');
        $.fn.Hashtag('bind', id, {
            'match': function() {
                nav.find("a[href='#" + id + "']").tab('show');
            }
        });
    });
});
