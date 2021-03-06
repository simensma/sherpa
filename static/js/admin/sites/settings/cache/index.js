$(function() {

    $("select[name='article'], select[name='page']").chosen();

    var table = $("table.delete-cache");

    table.find("button.main-menu").click(function() {
        $("div.delete-success span.name").text("Hovedmeny-cachen");
        deleteCache($(this), 'main-menu');
    });

    table.find("button.frontpage").click(function() {
        $("div.delete-success span.name").text("Forsidecachen");
        deleteCache($(this), 'frontpage');
    });

    table.find("button.page").click(function() {
        var id = $("select[name='page']").val();
        if(id == "" || isNaN(id)) {
            alert("Du må velge hvilken side du vil slette cachen for!");
            return;
        }
      $("div.delete-success span.name").text("Cachen for siden '" + $("select[name='page'] option:selected").text() + "'");
        deleteCache($(this), 'page', id);
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

    table.find("button.instagram").click(function() {
        $("div.delete-success span.name").text("Instagramfeed-cachen");
        deleteCache($(this), 'instagram');
    })

    function deleteCache(button, key, id) {
        button.hide();
        button.siblings("img.loader").show();
        $.ajaxQueue({
            url: table.attr('data-url'),
            data: {
                key: key,
                id: id
            }
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
