$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var dates = form.find("div.section.dates");

    var validators = [
        new TitleValidator(),
        new DescriptionValidator(),
        new DifficultyValidator(),
        new AudienceValidator(),
        new CategoryValidator(),
        new CountyValidator(),
        new MunicipalityValidator(),
        new DatesValidator(),
        new PublicationDateValidator(),
    ];

    (function(AktivitetValidator, $, undefined ) {

        AktivitetValidator.validate = function() {
            var valid = true;
            var scrollTo;

            for(var i=0; i<validators.length; i++) {
                var this_valid = validators[i].validate();
                valid = valid && this_valid;
                if(!valid) {
                    scrollTo = scrollTo || validators[i].scrollTo;
                }
            }

            return {
                valid: valid,
                scrollTo: scrollTo
            };
        };

    }(window.AktivitetValidator = window.AktivitetValidator || {}, jQuery ));

    /**
     * So we'll try a new take on clientside validations here. Check on focusout, and also
     * on submit, and in the latter case scroll to the first error. Define "static classes"
     * for each element to validate.
     */

    function TitleValidator() {
        var that = this;
        var control_group = form.find("div.control-group.title");
        var input = control_group.find("input[name='title']");
        var error = control_group.find("div.error");
        this.scrollTo = control_group.parents("div.section");

        this.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        input.focus(this.clearError);
        input.focusout(this.validate);
    }

    function DescriptionValidator() {
        var that = this;
        var control_group = form.find("div.control-group.description");
        var input = control_group.find("textarea[name='description']");
        var error = control_group.find("div.error");
        this.scrollTo = control_group.parents("div.section");

        this.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        input.focus(this.clearError);
        input.focusout(this.validate);
    }

    function DifficultyValidator() {
        var that = this;
        var control_group = form.find("div.control-group.difficulty");
        var select = control_group.find("select[name='difficulty']");
        var error = control_group.find("div.error");
        this.scrollTo = control_group;

        this.validate = function() {
            var valid = select.find("option:selected").val() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        select.change(this.clearError);
    }

    function AudienceValidator() {
        var that = this;
        var control_group = form.find("div.control-group.audiences");
        var select = control_group.find("select[name='audiences']");
        var error = control_group.find("div.error");
        this.scrollTo = control_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        select.change(function() {
            if(that.validate()) {
                that.clearError();
            }
        });
    }


    function CategoryValidator() {
        var that = this;
        var control_group = form.find("div.control-group.category, div.control-group.subcategories");
        var error = control_group.find("div.error");
        var category_buttons = control_group.find("button[data-category]");
        var subcategory_buttons = control_group.find("button.subcategory");
        this.scrollTo = control_group;

        this.validate = function() {
            var category = category_buttons.filter(".active").attr('data-category');
            var valid = subcategory_buttons.is("." + category + ".btn-danger");
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        category_buttons.click(this.clearError);
        subcategory_buttons.click(this.clearError);
    }

    function CountyValidator() {
        var that = this;
        var control_group = form.find("div.control-group.counties");
        var error = control_group.find("div.error");
        var select = control_group.find("select[name='counties']");
        this.scrollTo = control_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        select.change(function() {
            if(that.validate()) {
                that.clearError();
            }
        });
    }

    function MunicipalityValidator() {
        var that = this;
        var control_group = form.find("div.control-group.municipalities");
        var error = control_group.find("div.error");
        var select = control_group.find("select[name='municipalities']");
        this.scrollTo = control_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        select.change(function() {
            if(that.validate()) {
                that.clearError();
            }
        });
    }

    function PublicationDateValidator() {
        var that = this;
        var control_group = form.find("div.control-group.pub_date");
        var error = control_group.find("div.error");
        var date = control_group.find("div.date");
        var input = control_group.find("input[name='pub_date']");
        this.scrollTo = control_group;

        this.validate = function() {
            var valid = input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            control_group.addClass('error');
            error.show();
        };

        this.clearError = function() {
            control_group.removeClass('error');
            error.hide();
        };

        date.on('show', this.clearError);
        date.on('changeDate', this.validate);
        input.focus(this.clearError);
    }

    function DatesValidator() {

        /**
         * Note that a weak point here is that the focus events won't work until the first
         * attempt to validate (it won't be bound at runtime)
         */

        var that = this;
        this.scrollTo = undefined;

        this.validate = function() {
            var valid = true;
            dates.find("div.date-root:not(.hide)").each(function() {
                var view = $(this).data('view');

                var validators = [
                    new StartTimeValidator(view.root),
                    new EndTimeValidator(view.root),
                    new SignupStartValidator(view.root),
                    new SignupDeadlineValidator(view.root),
                    new SignupCancelDeadlineValidator(view.root),
                ];

                for(var i=0; i<validators.length; i++) {
                    var this_valid = validators[i].validate();

                    valid = valid && this_valid;
                    that.scrollTo = that.scrollTo || validators[i].scrollTo;

                    if(!this_valid) {
                        view.edit({instant: true});
                    }
                }
            });

            return valid;
        };

        // Start datetime format
        function StartTimeValidator(root) {

            var control_group = root.find("div.control-group.start_date");
            var error = control_group.find("div.error");
            var date_control = control_group.find("div.date");
            var date_input = control_group.find("input[name='start_date']");
            var time_input = control_group.find("input[name='start_time']");
            this.scrollTo = root;

            this.validate = function() {
                var date_valid = date_input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;
                var time_valid = time_input.val().match(/^\d\d:\d\d$/) !== null;
                var valid = date_valid && time_valid;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            date_input.focus(clearError);
            time_input.focus(clearError);
            date_control.on('changeDate', this.validate);
            time_input.focusout(this.validate);

            function markError() {
                control_group.addClass('error');
                error.show();
            }

            function clearError() {
                control_group.removeClass('error');
                error.hide();
            }
        }

        // End datetime format
        function EndTimeValidator(root) {

            var control_group = root.find("div.control-group.end_date");
            var error = control_group.find("div.error");
            var date_control = control_group.find("div.date");
            var date_input = control_group.find("input[name='end_date']");
            var time_input = control_group.find("input[name='end_time']");
            this.scrollTo = root;

            this.validate = function() {
                var date_valid = date_input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;
                var time_valid = time_input.val().match(/^\d\d:\d\d$/) !== null;
                var valid = date_valid && time_valid;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            date_input.focus(clearError);
            time_input.focus(clearError);
            date_control.on('changeDate', this.validate);
            time_input.focusout(this.validate);

            function markError() {
                control_group.addClass('error');
                error.show();
            }

            function clearError() {
                control_group.removeClass('error');
                error.hide();
            }
        }

        // End datetime format
        function SignupStartValidator(root) {

            var control_group_signup = root.find("div.control-group.signup");
            var control_group = root.find("div.control-group.signup_start");
            var error = control_group.find("div.error");
            var signup_start = control_group.find("div.date");
            var signup_start_input = control_group.find("input[name='signup_start']");
            this.scrollTo = root;

            this.validate = function() {

                if(control_group_signup.find("input:checked").is("[value='none']")) {
                    return true;
                }

                var valid = signup_start_input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            signup_start_input.focus(clearError);
            signup_start.on('show', clearError);
            signup_start.on('changeDate', this.validate);

            function markError() {
                control_group.addClass('error');
                error.show();
            }

            function clearError() {
                control_group.removeClass('error');
                error.hide();
            }
        }

        // End datetime format
        function SignupDeadlineValidator(root) {

            var control_group_signup = root.find("div.control-group.signup");
            var control_group = root.find("div.control-group.signup_deadline");
            var error = control_group.find("div.error");
            var signup_deadline_until_start = control_group.find("input[name='signup_deadline_until_start']");
            var signup_deadline = control_group.find("div.date");
            var signup_deadline_input = control_group.find("input[name='signup_deadline']");
            this.scrollTo = root;

            this.validate = function() {

                if(control_group_signup.find("input:checked").is("[value='none']")) {
                    return true;
                }

                if(signup_deadline_until_start.is(":checked")) {
                    return true;
                }

                var valid = signup_deadline_input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            signup_deadline_until_start.change(clearError);
            signup_deadline_input.focus(clearError);
            signup_deadline.on('show', clearError);
            signup_deadline.on('changeDate', this.validate);

            function markError() {
                control_group.addClass('error');
                error.show();
            }

            function clearError() {
                control_group.removeClass('error');
                error.hide();
            }
        }

        // End datetime format
        function SignupCancelDeadlineValidator(root) {

            var control_group_signup = root.find("div.control-group.signup");
            var control_group = root.find("div.control-group.signup_cancel_deadline");
            var error = control_group.find("div.error");
            var signup_cancel_deadline_until_start = control_group.find("input[name='signup_cancel_deadline_until_start']");
            var signup_cancel_deadline = control_group.find("div.date");
            var signup_cancel_deadline_input = control_group.find("input[name='signup_cancel_deadline']");
            this.scrollTo = root;

            this.validate = function() {

                if(control_group_signup.find("input:checked").is("[value='none']")) {
                    return true;
                }

                if(signup_cancel_deadline_until_start.is(":checked")) {
                    return true;
                }

                var valid = signup_cancel_deadline_input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            signup_cancel_deadline_until_start.change(clearError);
            signup_cancel_deadline_input.focus(clearError);
            signup_cancel_deadline.on('show', clearError);
            signup_cancel_deadline.on('changeDate', this.validate);

            function markError() {
                control_group.addClass('error');
                error.show();
            }

            function clearError() {
                control_group.removeClass('error');
                error.hide();
            }
        }

    }

});
