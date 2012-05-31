$(document).ready(function() {

    $("div.loading").hide();

    performSearch();
    $("input[type='radio']").change(performSearch);
    function performSearch() {
        var category = $("input[type='radio'][name='category']:checked").val();
        var county = $("input[type='radio'][name='county']:checked").val();
        $("div#results div.result").remove();
        if(category == 'all' && county == 'all') {
            $("div#results div.info").show();
            return $(this);
        } else {
            $("div#results div.info").hide();
        }
        $("div.loading").show();
        $.ajax({
            url: '/foreninger/filtrer/',
            type: 'POST',
            data: 'category=' + encodeURIComponent(category) +
                  '&county=' + encodeURIComponent(county)
        }).fail(function(result) {
            $(document.body).html(result.responseText);
        }).done(function(result) {
            result = JSON.parse(result);
            for(var i=0; i<result.length; i++) {
                $("div#results").append(result[i]);
            }
        }).always(function() {
            $("div.loading").hide();
        });
    }

});
