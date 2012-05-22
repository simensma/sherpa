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
            $("form#household img.ajaxloader").show();
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#household input[name='city']").val(result);
            }).fail(function(result) {
                $("form#household input[name='city']").val("Ukjent postnummer");
                $("form#household div.control-group.zipcode").addClass('error');
            }).always(function(result) {
                $("form#household img.ajaxloader").hide();
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
           !confirm("Har du virkelig ingen adresse?\n\nDet finnes enkelte husstander i Norge som kun har postnummer og -sted, uten gateadresse. Hvis du bor på en av disse kan du gå videre, hvis ikke, trykk avbryt og fyll inn adressen.")) {
                e.preventDefault();
        }
    });

});
