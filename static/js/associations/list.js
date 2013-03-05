$(document).ready(function() {

    $("div.loading").hide();
    $("div.count").hide();
    $("div.no-results").hide();

    $("select[name='full-list']").chosen().change(function() {
        var url = $(this).find("option:selected").val();
        if(url == 'ukjent') {
            alert('Beklager, denne foreningen/dette turlaget har ingen hjemmeside vi kan sende deg videre til.');
        } else {
            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }
            window.location = url;
        }
    });

    // Mark the initially checked labels
    function setActive() {
        $("label.active").removeClass('active');
        $("input[type='radio']:checked").each(function() {
            $(this).parent('label').addClass('active');
        });
    }

    setActive();
    var defaultCategory = $("input[type='radio'][name='category']:checked").val();
    var defaultCounty = $("input[type='radio'][name='county']:checked").val();
    performSearch(defaultCategory, defaultCounty);

    $("input[type='radio']").change(setActive);
    $("input[type='radio']").change(function() {
        var category = $("input[type='radio'][name='category']:checked").val();
        var county = $("input[type='radio'][name='county']:checked").val();
        performSearch(category, county);
    });

    $("select[name='category'], select[name='county']").change(function() {
        var category = $("select[name='category'] option:selected").val();
        var county = $("select[name='county'] option:selected").val();
        performSearch(category, county);
    });

    function performSearch(category, county) {
        $("table#results").children().remove();
        if(category == 'all' && county == 'all') {
            $("div.all").show();
            return $(this);
        } else {
            $("div.all").hide();
        }
        $("div.loading").show();
        $("div.count").hide();
        $("div.no-results").hide();
        $("div.syntaxerror").hide();
        $.ajaxQueue({
            url: '/foreninger/filtrer/',
            data: {
                category: category,
                county: county
            }
        }).fail(function(result) {
            $("div.syntaxerror").show();
        }).done(function(result) {
            // Remove results again just to ensure it's clean
            $("table#results").children().remove();
            try {
                result = JSON.parse(result);
                for(var i=0; i<result.length; i++) {
                    $("table#results").append(result[i]);
                }
                if(result.length == 0) {
                    $("div.no-results").show();
                }
                $("table#results div.map").hide();
                $("table#results a.close-map").hide();
                $("div.count").show();
                $("div.count span.count").text(result.length);
            } catch(SyntaxError) {
                // Not sure why this would ever happen?
                // I'd like to refresh the window and assume next try would work, but that
                // could lead to an infinite loop :) so just inform the user of an error.
                $("div.syntaxerror").show();
            }
        }).always(function() {
            $("div.loading").hide();
        });
    }
});
