(function(ZipcodeValidator, $, undefined ) {

    ZipcodeValidator.validate = function(control_group, zipcode, area, loader, options) {
        zipcode.on('focusin.zipcodevalidator', function() {
            control_group.removeClass('error success');
        });

        zipcode.on('focusout.zipcodevalidator', function() {
            validate(control_group);
        });

        zipcode.on('keyup.zipcodevalidator', function() {
            control_group.removeClass('success error');
            function end() {
                if(!zipcode.is(":focus")) {
                    validate(control_group);
                }
            }
            control_group.data('valid', false);
            if(!zipcode.val().match(/^\d{4}$/)) {
                end();
                return zipcode;
            }
            loader.show();
            $.ajax({
                url: '/postnummer/' + encodeURIComponent(zipcode.val()) + '/',
                type: 'POST'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.area != undefined) {
                    area.val(result.area);
                    control_group.addClass('success');
                    control_group.data('valid', true);
                } else if(result.error == "does_not_exist") {
                    area.val("Ukjent postnummer");
                    control_group.addClass('error');
                }
            }).fail(function(result) {
                area.val("Teknisk feil");
                control_group.addClass('error');
            }).always(function(result) {
                loader.hide();
                end();
            });
        });
    }

    ZipcodeValidator.trigger = function(zipcode) {
        zipcode.keyup();
    }

    ZipcodeValidator.stopValidation = function(zipcode) {
        zipcode.off('focusin.zipcodevalidator focusout.zipcodevalidator keyup.zipcodevalidator');
    }

    function validate(control_group) {
        control_group.removeClass('error success');
        if(control_group.data('valid')) {
            control_group.addClass('success');
        } else {
            control_group.addClass('error');
        }
    }

}(window.ZipcodeValidator = window.ZipcodeValidator || {}, jQuery ));
