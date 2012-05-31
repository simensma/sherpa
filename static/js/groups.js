$(document).ready(function() {

    $("div.loading").hide();

    performSearch();
    $("input[type='radio']").change(performSearch);
    function performSearch() {
        var category = $("input[type='radio'][name='category']:checked").val();
        var county = $("input[type='radio'][name='county']:checked").val();
        $("table#results").children().remove();
        if(category == 'all' && county == 'all') {
            $("div.all").show();
            return $(this);
        } else {
            $("div.all").hide();
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
                $("table#results").append(result[i]);
            }
        }).always(function() {
            $("div.loading").hide();
        });
    }

});
