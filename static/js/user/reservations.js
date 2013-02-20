$(document).ready(function() {

    var table = $("table.user-reservations");

    function setActive() {
        table.find("tr.active").removeClass('active');
        table.find("input[type='radio']:checked").each(function() {
            $(this).parents('tr').addClass('active');
        });
    }

    table.find("td.fake-table-label").click(function() {
        var radio = $(this).parent().find("input[type='radio']");
        if(!radio.is(":checked")) {
            radio.prop('checked', true).change();
        }
    });

    table.find("input[type='radio']").change(setActive);
    table.find("input[type='radio'][name='sponsors']").change(function() {
        var this_table = $(this).parents("table");
        this_table.find("tr.status").hide();
        this_table.find("tr.loading").show();
        var reserve = $(this).val() == 'reserve';
        $.ajaxQueue({
            url: this_table.attr('data-url'),
            data: { reserve: reserve }
        }).done(function() {
            if(reserve) {
                this_table.find("span.success").hide().filter(".reserve").show();
            } else {
                this_table.find("span.success").hide().filter(".allow").show();
            }
            this_table.find("tr.success").show();
        }).fail(function() {
            this_table.find("tr.error").show();
            // Setting prop shouldn't trigger 'change'. Note that a trigger would yield an infinite loop.
            this_table.find("input[type='radio']:not(:checked)").prop('checked', true);
            setActive();
        }).always(function() {
            this_table.find("tr.loading").hide();
        });
    });


    setActive();
});
