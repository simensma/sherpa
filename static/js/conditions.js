$(document).ready(function() {
    var filter = $("select[name='conditions-filter']");

    filter.chosen({
        'allow_single_deselect': true
    });
    filter.change(function() {
        var selected = $(this).find("option:selected").val();
        if(selected === '') {
            $("div.conditions").show();
            return $(this);
        }

        $("div.conditions").each(function() {
            var ids = JSON.parse($(this).attr("data-locations"));
            var show = false;
            for(var i=0; i<ids.length; i++) {
                if(ids[i] == selected) {
                    show = true;
                }
            }
            if(show) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
});
