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
        if(methods[opts.method](opts.input.val(), opts.req, opts.opts)) {
            opts.control_group.removeClass('error').addClass('success');
        } else {
            opts.control_group.removeClass('success').addClass('error');
        }
    }

    var methods = {
        'full_name': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^.+\s.+$/) != null;
        },
        'address': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/[^\s]/) != null;
        },
        'phone': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.length >= 8 && input.match(/[a-z]/i) == null;
        },
        'email': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^\s*[^\s]+@[^\s]+\.[^\s]+\s*$/) != null;
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

}(window.Validator = window.Validator || {}, jQuery ));
