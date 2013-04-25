$(document).ready(function() {

    var editor = $("div.edit-aktivitet-dates");

    function enableDatepicker(elements) {
        elements.datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            autoclose: true,
            language: 'nb'
        });
    }

    // Long selectors make you feel alive
    enableDatepicker(editor.find("div.control-group.start_date div.date,div.control-group.end_date div.date,div.control-group.signup_start div.date,div.control-group.signup_deadline div.date,div.control-group.signup_cancel_deadline div.date,div.control-group.pub_date div.date"));

    // Hide signup-options (for each date) if signup is disabled
    $(document).on('click', editor.selector + ' div.control-group.signup_enabled button', function() {
        var signup_enabled = $(this).parents("div.controls").find("input[name='signup_enabled']");
        var signup_details = $(this).parents("div.control-group").siblings("div.signup-details");
        if($(this).is(".enable")) {
            signup_details.slideDown();
            signup_enabled.find("input[name='signup_enabled']").val(JSON.stringify(true));
        } else if($(this).is(".disable")) {
            signup_details.slideUp();
            signup_enabled.find("input[name='signup_enabled']").val(JSON.stringify(false));
        }
    });

    // Enable date-editing
    $(document).on('click', editor.selector + ' div.aktivitet-date div.summary a.edit-date', function() {
        var summary = $(this).parents("div.summary");
        summary.hide();
        summary.siblings("div.editing").attr("data-active", "").slideDown();
    });

    // Delete a date
    $(document).on('click', editor.selector + ' div.aktivitet-date div.summary a.delete-date', function() {
        // TODO: If the dates have participants, give a warning that the participants
        // should be notified about the date change
        if(editor.find("div.aktivitet-date").length == 1) {
            alert("Turen må ha minst én dato! Du kan ikke slette denne siste datoen.");
            return $(this);
        }
        if(!confirm("Er du helt sikker på at du vil slette disse datoene?")) {
            return $(this);
        }
        var url = $(this).attr('data-url');
        var date_wrapper = $(this).parents("div.aktivitet-date");
        var management_rows = $(this).parents("table").find("tr.management");
        var ajaxloader_row = $(this).parents("table").find("tr.ajaxloader");
        management_rows.hide();
        ajaxloader_row.show();
        $.ajaxQueue({
            url: url
        }).done(function() {
            date_wrapper.slideUp({
                complete: function() {
                    $(this).remove();
                }
            });
        }).fail(function() {
            alert("Beklager - det oppstod en feil når vi prøvde å slette disse datoene!\n\n" +
                "Har du sjekket at du ikke har mistet tilgang til internett?\n\n" +
                "Du kan prøve igjen så mange ganger du vil. Feilen har blitt logget i våre systemer, og hvis vi ser at det er en feil i Sherpa så skal vi rette den så snart som mulig.");
            management_rows.show();
            ajaxloader_row.hide();
        });
    });

    // Add new date
    editor.find("a.add-aktivitet-date").click(function() {
        var url = $(this).attr('data-url');
        var aktivitet_id = editor.attr('data-aktivitet-id');
        var anchor = $(this);
        var ajaxloader = $(this).siblings("img.ajaxloader");
        anchor.hide();
        ajaxloader.show();
        $.ajaxQueue({
            url: url,
            data: { aktivitet: aktivitet_id }
        }).done(function(result) {
            result = $(JSON.parse(result));
            result.addClass('hide');
            editor.find("div.aktivitet-date").last().after(result);
            enableDatepicker(result.find("div.input-append.date"));
            result.find("div.summary").hide();
            result.find("div.editing").attr('data-active', '').show();
            result.slideDown();
        }).fail(function() {
            alert("Beklager - det oppstod en feil når vi prøvde å opprette en ny dato for denne turen!\n\n" +
                "Har du sjekket at du ikke har mistet tilgang til internett?\n\n" +
                "Du kan prøve igjen så mange ganger du vil. Feilen har blitt logget i våre systemer, og hvis vi ser at det er en feil i Sherpa så skal vi rette den så snart som mulig.");
        }).always(function() {
            anchor.show();
            ajaxloader.hide();
        });
    });

    // On date save
    $(document).on('click', editor.selector + ' div.aktivitet-date div.editing button.save-date', function() {
        var editing = $(this).parents("div.editing");
        var signup_enabled = editing.find("div.control-group.signup_enabled button.active").is(".enable");
        var button = $(this);
        var ajaxloader = $(this).siblings("img.ajaxloader");
        button.hide();
        ajaxloader.show();
        $.ajaxQueue({
            url: editing.attr('data-url'),
            data: {
                start_date: editing.find("input[name='start_date']").val(),
                start_time: editing.find("input[name='start_time']").val(),
                end_date: editing.find("input[name='end_date']").val(),
                end_time: editing.find("input[name='end_time']").val(),
                signup_enabled: JSON.stringify(signup_enabled),
                signup_start: editing.find("input[name='signup_start']").val(),
                signup_deadline: editing.find("input[name='signup_deadline']").val(),
                signup_cancel_deadline: editing.find("input[name='signup_cancel_deadline']").val()
            }
        }).done(function(result) {
            result = $(JSON.parse(result));
            result.addClass('hide');
            editing.parents("div.aktivitet-date").replaceWith(result);
            enableDatepicker(result.find("div.input-append.date"));
            result.slideDown();
        }).fail(function() {
            alert("Beklager - det oppstod en feil når vi prøvde å lagre datoene!\n\n" +
                "Har du sjekket at du ikke har mistet tilgang til internett?\n\n" +
                "Du kan prøve å lagre igjen så mange ganger du vil, men husk at hvis du lukker siden så mister du endringene dine!\n\n" +
                "Feilen har blitt logget i våre systemer, og hvis vi ser at det er en feil i Sherpa så skal vi rette den så snart som mulig.");
            button.show();
            ajaxloader.hide();
        });
    });

});
