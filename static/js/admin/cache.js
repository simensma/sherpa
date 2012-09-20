$(document).ready(function() {

    $("select[name='article']").chosen();

    $("button.frontpage").click(function() {
        deleteCache(this, 'frontpage');
    });

    $("button.article").click(function() {
        var id = $("select[name='article']").val();
        if(isNaN(id)) {
            alert("Du må velge hvilken artikkel du vil slette cachen for!");
            return;
        }
        deleteCache(this, 'article', id);
    });

    $("button.main-menu").click(function() {
        deleteCache(this, 'main-menu');
    });

    function deleteCache(button, key, article) {
        $(button).attr('disabled', true);
        $.ajax({
            url: '/sherpa/cache/slett/',
            data: 'key=' + encodeURIComponent(key) + '&article=' + encodeURIComponent(article)
        }).done(function() {
            alert("Cachen har blitt sletta, du kan nå besøke siden for oppdatert versjon.");
        }).always(function() {
            $(button).removeAttr('disabled');
        });
    }

});
