(function(Validator, $, undefined ) {

    var triggers = [];

    // Manually trigger all validations
    Validator.trigger = function() {
        for(var i=0; i<triggers.length; i++) {
            triggers[i]();
        }
    }

    Validator.validate = function(opts) {
        // Save a list of how to manually trigger validations
        triggers.push(function() { opts.input.focusout(); });

        // Clear status on focusin
        opts.input.on('focusin.validator', function() {
            opts.control_group.removeClass('error success');
        });

        // Perform the validation on focusout
        opts.input.on('focusout.validator', function() { Validator.performValidation(opts); });
    }

    Validator.performValidation = function(opts) {
        if(Validator.check[opts.method](opts.input.val(), opts.req, opts.opts)) {
            opts.control_group.removeClass('error').addClass('success');
        } else {
            opts.control_group.removeClass('success').addClass('error');
        }
    }

    Validator.check = {
        'full_name': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^.+\s.+$/) != null;
        },
        'address': function(input, req, opts) {
            if(!req && input == '') { return true; }
            var res = input.match(/[^\s]/) != null;
            if(opts !== undefined && opts.hasOwnProperty('max_length')) {
                if(input.length >= opts.max_length) {
                    res = false;
                }
            }
            return res;
        },
        'phone': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.length >= 8 && input.match(/[a-z]/i) == null;
        },
        'email': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^\s*[^\s\,\<\>]+@[^\s,\<\>]+\.[^\s,\<\>]+\s*$/) != null;
        },
        'memberid': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^\d+$/) != null;
        },
        'date': function(input, req, opts) {
            if(!req && input == '') { return true; }
            var res;
            res = input.match(/^\d\d\.\d\d\.\d\d\d\d$/) != null;
            if(opts != undefined && opts.hasOwnProperty('min_year')) {
                if(Number(input.substring(6)) < opts['min_year']) {
                    res = false;
                }
            }
            return res;
        },
        'anything': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/[^\s]+/) != null;
        }
    };


    /**
     * Zipcode-validation with AJAX-lookup
     */
    Validator.triggerZipcode = function(zipcode) { zipcode.keyup(); }
    Validator.stopZipcodeValidation = function(zipcode) { zipcode.off('.zipcodevalidator'); }
    Validator.validateZipcode = function(control_group, zipcode, area, loader, options) {

        zipcode.on('focusin.zipcodevalidator', function() {
            control_group.removeClass('error success');
        });

        zipcode.on('focusout.zipcodevalidator', function() {
            control_group.removeClass('error success');
            if(control_group.data('valid')) {
                control_group.addClass('success');
            } else {
                control_group.addClass('error');
            }
        });

        zipcode.on('keyup.zipcodevalidator', function() {
            control_group.removeClass('success error');
            function end() {
                if(!zipcode.is(":focus")) {
                    // Trigger validation-check
                    zipcode.focusout();
                }
            }
            control_group.data('valid', false);
            if(!zipcode.val().match(/^\d{4}$/)) {
                end();
                return zipcode;
            }
            loader.show();
            $.ajaxQueue({
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

    /**
     * Password-validator
     */
     Validator.validatePasswords = function(opts) {

         opts.pass1.on('focusin.passwordvalidator', function() { opts.control_group.removeClass('error success'); opts.hints.hide(); });
         opts.pass2.on('focusin.passwordvalidator', function() { opts.control_group.removeClass('error success'); opts.hints.hide(); });

         opts.pass1.on('focusout.passwordvalidator', function() {
             var len = checkLength(opts);
             // If length is invalid, just complain about that.
             // If not, check if pass2 is filled out. If it is, check for equality, but if not,
             // the user might just not have gotten to the second field, so don't say anything
             // about validity yet.
             if(len && opts.pass2.val() != '' && checkEquality(opts)) {
                 opts.control_group.removeClass('error').addClass('success');
             }
         });

         opts.pass2.on('focusout.passwordvalidator', function() {
             if(checkLength(opts) && checkEquality(opts)) {
                 opts.control_group.removeClass('error').addClass('success');
                 opts.hints.hide();
             }
         });


         function checkEquality(opts) {
             if(opts.pass1.val() != opts.pass2.val()) {
                 opts.control_group.removeClass('success').addClass('error');
                 opts.hints.filter(".unequal").show();
                 return false;
             }
             return true;
         }

         function checkLength(opts) {
             if(opts.pass1.val().length < opts.min_length) {
                 opts.control_group.removeClass('success').addClass('error');
                 opts.hints.filter(".short").show();
                 return false;
             }
             return true;
         }

     }

}(window.Validator = window.Validator || {}, jQuery ));
