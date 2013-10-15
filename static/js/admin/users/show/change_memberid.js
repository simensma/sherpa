$(document).ready(function() {

    /**
     * Changing memberid for a user
     */

    var change_memberid = $("div.change-memberid");
    var initiation = change_memberid.find("a.change-memberid");
    var form = change_memberid.find("form");
    var input = form.find("input[name='new-memberid']");
    var step1 = form.find("div.step1");
    var step2 = form.find("div.step2");
    var check = step1.find("p.check");
    var check_button = check.find("button.check");
    var loading = step1.find("div.loading");
    var error = step1.find("div.alert.alert-error");

    initiation.click(function() {
        $(this).hide();
        form.slideDown();
    });

    check_button.click(function(e) {
        input.prop('readonly', true);
        check.hide();
        loading.show();
        step2.empty();
        error.hide();
        e.preventDefault();

        $.ajaxQueue({
            url: check_button.attr('data-check-url'),
            data: {
                user: check_button.attr('data-user-id'),
                memberid: input.val()
            }
        }).done(function(result) {
            result = JSON.parse(result);
            step2.append($.parseHTML(result.html));
            if(!result.valid) {
                check.show();
                input.prop('readonly', false);
            }
        }).fail(function(result) {
            check.show();
            error.show();
            input.prop('readonly', false);
        }).always(function(result) {
            loading.hide();
        });
    });

    form.submit(function(e) {
        if(!confirm("Er du helt sikker på at du vil flytte all informasjon over til det nye medlemsnummeret, og slette det gamle?")) {
            e.preventDefault();
        }
    });

});
