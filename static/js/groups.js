$(document).ready(function() {

    $("div.loading").hide();

    $("input[type='radio']").change(function() {
        var category = $("input[type='radio'][name='category']:checked").val();
        var county = $("input[type='radio'][name='county']:checked").val();
        $("div#results").children().remove();
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
                var html = $('<div class="result"></div>');
                html.append('<h1>' + result[i].fields.name + '</h1>');
                html.append('<a href="' + result[i].fields.url + '">' + result[i].fields.url + '</a>');
                html.append('<p>E-post: <a href="mailto:' + result[i].fields.email + '">' + result[i].fields.email + '</a></p>');
                $("div#results").append(html);
            }
        }).always(function() {
            $("div.loading").hide();
        });
    });

});
