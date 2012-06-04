$(document).ready(function() {

    $("form#household div.household").hide();
    $("form#household input[name='household']").click(function() {
        if($(this).prop('checked')) {
            $("form#household div.household").show();
        } else {
            $("form#household div.household").hide();
        }
    });

    $("form#household img.ajaxloader").hide();
    $("form#household input[name='zipcode']").keyup(searchZip);
    if($("form#household select[name='country'] option:selected").val() == 'NO') {
        $("form#household input[name='zipcode']").keyup();
    }

    function searchZip() {
        if($(this).val().match(/^\d{4}$/)) {
            $("form#household img.zip.ajaxloader").show();
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.location != undefined) {
                    $("form#household input[name='city']").val(result.location);
                    $("form#household div.control-group.zipcode").removeClass('error');
                } else if(result.error == "does_not_exist") {
                    $("form#household input[name='city']").val("Ukjent postnummer");
                    $("form#household div.control-group.zipcode").addClass('error');
                }
            }).fail(function(result) {
                $("form#household input[name='city']").val("Teknisk feil");
                $("form#household div.control-group.zipcode").addClass('error');
            }).always(function(result) {
                $("form#household img.zip.ajaxloader").hide();
            });
        } else {
            $("form#household input[name='city']").val("");
        }
    }

    $("form#household select[name='country']").change(setAddressState);
    setAddressState();
    function setAddressState() {
        var sel = $("form#household select[name='country'] option:selected");
        if(sel.val() == 'NO') {
            $("form#household div.world").hide();
            $("form#household div.scandinavia").show();
            $("form#household div.yearbook").hide();
            $("form#household input[name='city']").attr('disabled', true);
            $("form#household input[name='zipcode']").keyup(searchZip);
            $("form#household input[name='zipcode']").keyup();
        } else if(sel.parents("optgroup#scandinavia").length > 0) {
            $("form#household div.world").hide();
            $("form#household div.scandinavia").show();
            $("form#household div.yearbook").show();
            $("form#household input[name='city']").removeAttr('disabled');
            $("form#household input[name='zipcode']").off('keyup');
        } else {
            $("form#household div.world").show();
            $("form#household div.scandinavia").hide();
            $("form#household div.yearbook").show();
        }
    }

    $("form#household input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning');
    });

    $("form#household input[name='address1']").focusout(function() {
        if($(this).val() == "") {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#household input[name='zipcode']").focusout(function() {
        if($("form#household select[name='country'] option:selected").val() == 'NO') {
            if(!$(this).val().match(/\d{4}/)) {
                $(this).parents("div.control-group").addClass('error');
            }
        } else {
            if($(this).val() == '') {
                $(this).parents("div.control-group").addClass('error');
            }
        }
    });

    $("form#household").submit(function(e) {
        if($(this).find("input[name='address1']").val() == '' &&
           $("form#household select[name='country'] option:selected").val() == 'NO' &&
           !confirm("Har du glemt å fylle ut gateadressen?\n\nHvis du ikke har gateadresse, klikker du bare OK for å gå videre.")) {
                e.preventDefault();
        }
    });

    /* Existing */
    $("form#household button.search").click(function(e) {
        e.preventDefault();
        $("div.existing-result").show();
        var button = $(this);
        button.attr('disabled', true);
        $("form#household img.existing.ajaxloader").show();
        var data = {
            id: $("form#household input[name='existing']").val(),
            zipcode: $("form#household input[name='zipcode']").val(),
            country: $("form#household select[name='country'] option:selected").val()
        }
        $("div.existing-result span.result").hide();
        $("div.existing-result span.result").removeClass('success');
        $("div.existing-result span.result").removeClass('error');
        $.ajax({
            url: '/innmelding/eksisterende/',
            type: 'POST',
            data: 'data=' + encodeURIComponent(JSON.stringify(data))
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'bad_zipcode') {
                $("div.existing-result span.result").text("Du må oppgi riktig postnummer før du søker.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'invalid_id') {
                $("div.existing-result span.result").text("Ugyldig medlemsnummer oppgitt.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actor.does_not_exist') {
                $("div.existing-result span.result").text("Fant ingen medlemmer med dette medlemsnummeret.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actor.too_young') {
                $("div.existing-result span.result").text("Det angitte medlemmet er bare " + result.age + " år ved utgangen av året, og kan ikke være hovedmedlem.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actoraddress.does_not_exist') {
                $("div.existing-result span.result").text("Det angitte medlemmet bor ikke på samme adresse som dere.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.name != '') {
                $("div.existing-result span.result").text(result.name + ', ' + result.address);
                $("div.existing-result span.description").show();
                $("div.existing-result span.result").addClass('success');
            }
        }).fail(function(result) {
            $(document.body).html(result.responseText);
        }).always(function() {
            button.removeAttr('disabled');
            $("form#household img.existing.ajaxloader").hide();
            $("div.existing-result span.result").show();
        });
    });

    if(existing) {
        $("form#household button.search").click();
    } else {
        $("div.existing-result").hide();
    }

});
