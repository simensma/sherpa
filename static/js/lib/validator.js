(function(Validator, $, undefined ) {

    var triggers = [];

    // Manually trigger all validations
    Validator.trigger = function() {
        for(var i=0; i<triggers.length; i++) {
            triggers[i]();
        }
    };

    Validator.validate = function(opts) {
        // Save a list of how to manually trigger validations
        triggers.push(function() { opts.input.focusout(); });

        // Clear status on focusin
        opts.input.on('focusin.validator', function() {
            opts.form_group.removeClass('has-error has-success');
        });

        // Perform the validation on focusout
        opts.input.on('focusout.validator', function() { Validator.performValidation(opts); });
    };

    Validator.performValidation = function(opts) {
        if(Validator.check[opts.method](opts.input.val(), opts.req, opts.opts)) {
            opts.form_group.removeClass('has-error').addClass('has-success');
        } else {
            opts.form_group.removeClass('has-success').addClass('has-error');
        }
    };

    Validator.check = {
        'full_name': function(input, req, opts) {
            if(!req && input === '') { return true; }
            return input.match(/^.+\s.+$/) !== null;
        },
        'address': function(input, req, opts) {
            if(!req && input === '') { return true; }
            var res = input.match(/[^\s]/) !== null;
            if(opts !== undefined && opts.hasOwnProperty('max_length')) {
                if(input.length >= opts.max_length) {
                    res = false;
                }
            }
            return res;
        },
        'phone': function(input, req, opts) {
            if(!req && input === '') { return true; }
            return input.length >= 8 && input.match(/[a-z]/i) === null;
        },
        'email': function(input, req, opts) {
            if(!req && input === '') { return true; }
            var email_format = input.match(/^\s*[^\s\,\<\>]+@[^\s,\<\>]+\.[^\s,\<\>]+\s*$/) !== null;
            var no_dotdot = !input.contains("..");
            var no_double_at = input.indexOf("@") == input.lastIndexOf("@");
            var input_trimmed = input.trim();
            var no_leading_dot;
            var no_trailing_dot;
            if(input_trimmed.length > 0) {
                no_leading_dot = input_trimmed[0] !== '.';
                no_trailing_dot = input_trimmed[input_trimmed.length-1] !== '.';
            } else {
                no_leading_dot = true;
                no_trailing_dot = true;
            }
            return (email_format && no_dotdot && no_double_at && no_leading_dot && no_trailing_dot);
        },
        'memberid': function(input, req, opts) {
            if(!req && input === '') { return true; }
            return input.match(/^\d+$/) !== null;
        },
        'date': function(input, req, opts) {
            if(!req && input === '') { return true; }
            var res;
            res = input.match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;
            if(opts !== undefined && opts.hasOwnProperty('min_year')) {
                if(Number(input.substring(6)) < opts['min_year']) {
                    res = false;
                }
            }
            if(opts !== undefined && opts.hasOwnProperty('max_year')) {
                if(Number(input.substring(6)) > opts['max_year']) {
                    res = false;
                }
            }
            return res;
        },
        'anything': function(input, req, opts) {
            if(!req && input === '') { return true; }
            return input.match(/[^\s]+/) !== null;
        }
    };


    /**
     * Zipcode-validation with AJAX-lookup
     */
    Validator.triggerZipcode = function(zipcode) { zipcode.keyup(); };
    Validator.stopZipcodeValidation = function(zipcode) { zipcode.off('.zipcodevalidator'); };
    Validator.validateZipcode = function(form_group, zipcode, area, loader, options) {

        zipcode.on('focusin.zipcodevalidator', function() {
            form_group.removeClass('has-error has-success');
        });

        zipcode.on('focusout.zipcodevalidator', function() {
            form_group.removeClass('has-error has-success');
            if(form_group.data('valid')) {
                form_group.addClass('has-success');
            } else {
                form_group.addClass('has-error');
            }
        });

        zipcode.on('keyup.zipcodevalidator', function() {
            form_group.removeClass('has-success has-error');
            function end() {
                if(!zipcode.is(":focus")) {
                    // Trigger validation-check
                    zipcode.focusout();
                }
            }
            form_group.data('valid', false);
            if(!zipcode.val().match(/^\d{4}$/)) {
                end();
                return zipcode;
            }
            loader.show();
            LookupZipcode(zipcode.val(), function(result) {
                if(result.success) {
                    area.val(result.area);
                    form_group.addClass('has-success');
                    form_group.data('valid', true);
                } else if(result.error == 'does_not_exist') {
                    area.val("Ukjent postnummer");
                    form_group.addClass('has-error');
                } else if(result.error == 'technical_failure') {
                    area.val("Teknisk feil");
                    form_group.addClass('has-error');
                }
                loader.hide();
                end();
            });
        });
    };

    /**
     * Password-validator
     */
     Validator.validatePasswords = function(opts) {

         opts.pass1.on('focusin.passwordvalidator', function() { opts.form_group.removeClass('has-error has-success'); opts.help_blocks.hide(); });
         opts.pass2.on('focusin.passwordvalidator', function() { opts.form_group.removeClass('has-error has-success'); opts.help_blocks.hide(); });

         opts.pass1.on('focusout.passwordvalidator', function() {
             var len = checkLength(opts);
             // If length is invalid, just complain about that.
             // If not, check if pass2 is filled out. If it is, check for equality, but if not,
             // the user might just not have gotten to the second field, so don't say anything
             // about validity yet.
             if(len && opts.pass2.val() !== '' && checkEquality(opts)) {
                 opts.form_group.removeClass('has-error').addClass('has-success');
             }
         });

         opts.pass2.on('focusout.passwordvalidator', function() {
             if(checkLength(opts) && checkEquality(opts)) {
                 opts.form_group.removeClass('has-error').addClass('has-success');
                 opts.help_blocks.hide();
             }
         });


         function checkEquality(opts) {
             if(opts.pass1.val() != opts.pass2.val()) {
                 opts.form_group.removeClass('has-success').addClass('has-error');
                 opts.help_blocks.filter(".unequal").show();
                 return false;
             }
             return true;
         }

         function checkLength(opts) {
             if(opts.pass1.val().length < opts.min_length) {
                 opts.form_group.removeClass('has-success').addClass('has-error');
                 opts.help_blocks.filter(".short").show();
                 return false;
             }
             return true;
         }

     };

}(window.Validator = window.Validator || {}, jQuery ));
