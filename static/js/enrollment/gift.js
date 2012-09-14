$(document).ready(function() {
    $("form#gift").hide();
    $("div.gift-choice").click(function() {
        $("div.gift-choice").removeClass('active');
        $(this).addClass('active');
        $("p.type-display span").hide();
        $("p.type-display span." + $(this).attr('data-name')).show();
        $("form#gift").show();
    });

    $("form#gift input.zipcode").keyup(function() {
        var self = $(this);
        if(self.val().match(/^\d{4}$/)) {
            self.siblings("img.ajaxloader").show();
            $.ajaxQueue({
                url: '/postnummer/' + encodeURIComponent(self.val()) + '/',
                type: 'POST'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.location != undefined) {
                    self.siblings("input.city").val(result.location);
                    self.parents("div.control-group").removeClass('error').addClass('success');
                } else if(result.error == "does_not_exist") {
                    self.siblings("input.city").val("Ukjent postnummer");
                    self.parents("div.control-group").removeClass('success').addClass('error');
                }
            }).fail(function(result) {
                self.siblings("input.city").val("Teknisk feil");
                self.parents("div.control-group.zipcode").removeClass('success').addClass('error');
            }).always(function(result) {
                self.siblings("img.ajaxloader").hide();
            });
        } else {
            self.siblings("input.city").val("");
        }
    });

    $("form#gift input[name='receiver_dob']").datepicker({
        changeMonth: true,
        changeYear: true,
        firstDay: 1,
        yearRange: "1900:c",
        dateFormat: 'dd.mm.yy',
        dayNames: ['Søndag', 'Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag'],
        dayNamesShort: ['Søn', 'Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør'],
        dayNamesMin: ['Sø', 'Ma', 'Ti', 'On', 'To', 'Fr', 'Lø'],
        monthNames: ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August',
          'September', 'Oktober', 'November', 'Desember'],
        monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt',
          'Nov', 'Des'],
        defaultDate: '-15y',
        showOn: 'both',
        buttonImage: '/static/img/calendar.png',
        buttonImageOnly: true,
        buttonText: 'Velg dato...',
        onClose: validateDatepicker
    });

    // Clear input validation-status upon focus
    $("form#gift input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    var validator = new Validator();

    // Generic validation-complete function for most of the controls
    function markInput(el, valid) {
        if(valid) {
            el.parents("div.control-group").addClass('success');
        } else {
            el.parents("div.control-group").addClass('error');
        }
    }

    function markInputZipcode(el, valid) {
        if(!valid) {
            el.parents("div.control-group").addClass('error');
        }
        // Ignore if valid, let ajax mark it based on zipcode lookup
    }

    validator.addValidation('full_name', $("form#gift input[name='giver_name']"), markInput, true);
    validator.addValidation('address', $("form#gift input[name='giver_address']"), markInput, true);
    validator.addValidation('zipcode', $("form#gift input[name='giver_zipcode']"), markInputZipcode, true);
    validator.addValidation('memberno', $("form#gift input[name='giver_memberno']"), markInput, false);
    validator.addValidation('phone', $("form#gift input[name='giver_phone']"), markInput, false);
    validator.addValidation('email', $("form#gift input[name='giver_email']"), markInput, false);

    validator.addValidation('full_name', $("form#gift input[name='receiver_name']"), markInput, true);
    validator.addValidation('address', $("form#gift input[name='receiver_address']"), markInput, true);
    validator.addValidation('zipcode', $("form#gift input[name='receiver_zipcode']"), markInputZipcode, true);
    validator.addValidation('phone', $("form#gift input[name='receiver_phone']"), markInput, false);
    validator.addValidation('email', $("form#gift input[name='receiver_email']"), markInput, false);

    function validateDatepicker() {
        // Datepicker calls this on close
        markInput($(this), validator.validate('date', $("form#gift input[name='receiver_dob']").val(), true));
    }

});
