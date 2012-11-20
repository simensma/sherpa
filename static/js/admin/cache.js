$(document).ready(function() {

    $("select[name='article']").chosen();

    var table = $("table.delete-cache");

    table.find("button.main-menu").click(function() {
        $("div.delete-success span.name").text("Hovedmeny-cachen");
        deleteCache($(this), 'main-menu');
    });

    table.find("button.frontpage").click(function() {
        $("div.delete-success span.name").text("Forsidecachen");
        deleteCache($(this), 'frontpage');
    });

    table.find("button.blog-widget").click(function() {
        $("div.delete-success span.name").text("Bloggwidget-cachen");
        deleteCache($(this), 'blog-widget');
    });

    table.find("button.article").click(function() {
        var id = $("select[name='article']").val();
        if(id == "" || isNaN(id)) {
            alert("Du må velge hvilken artikkel du vil slette cachen for!");
            return;
        }
      $("div.delete-success span.name").text("Cachen for artikkelen '" + $("select[name='article'] option:selected").text() + "'");
        deleteCache($(this), 'article', id);
    });

    function deleteCache(button, key, article) {
        button.hide();
        button.siblings("img.loader").show();
        $.ajaxQueue({
            url: '/sherpa/cache/slett/',
            data: 'key=' + encodeURIComponent(key) + '&article=' + encodeURIComponent(article)
        }).done(function() {
            var success = $("div.delete-success");
            if(success.is(":hidden")) {
                success.slideDown();
            } else {
                success.hide().slideDown();
            }
        }).always(function() {
            button.show();
            button.siblings("img.loader").hide();
        });
    }

});
