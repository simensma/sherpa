var Validator = function() {
    this.validations = [];
    this.methods = {
        'full_name': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^.+\s.+$/) != null;
        },
        'address': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/[^\s]/) != null;
        },
        'zipcode': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^\d{4}$/) != null;
        },
        'phone': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.length >= 8 && input.match(/[a-z]/i) == null;
        },
        'email': function(input, req, opts) {
            if(!req && input == '') { return true; }
            return input.match(/^\s*[^\s]+@[^\s]+\.[^\s]+\s*$/) != null;
        },
        'memberno': function(input, req, opts) {
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
        }
    };
}

Validator.prototype.addValidation = function(method, el, complete, req, opts) {
    var self = this;
    self.validations.push({
        'method': method,
        'el': el,
        'req': req,
        'opts': opts
    });
    el.focusout(function() {
        complete(el, self.validate(method, el.val(), req, opts));
    });
}

Validator.prototype.validate = function(method, input, req, opts) {
    if(!this.methods.hasOwnProperty(method)) {
        throw new Error("Tried to validate with unknown validation method: " + method);
    }
    return this.methods[method](input, req, opts);
}

Validator.prototype.validateEverything = function() {
    var self = this;
    var ret = true;
    for(var i=0; i<self.validations.length; i++) {
        if(!self.validate(self.validations[i].method,
                          self.validations[i].el.val(),
                          self.validations[i].req,
                          self.validations[i].opts)) {
            ret = false;
        }
    }
    return ret;
}
