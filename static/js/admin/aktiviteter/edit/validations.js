$(function() {

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
        var form_group = form.find("div.form-group.title");
        var input = form_group.find("input[name='title']");
        var error = form_group.find("div.error");
        this.scrollTo = form_group.parents("div.section");

        this.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
            error.hide();
        };

        input.focus(this.clearError);
        input.focusout(this.validate);
    }

    function DescriptionValidator() {
        var that = this;
        var form_group = form.find("div.form-group.description");
        var input = form_group.find("textarea[name='description']");
        var error = form_group.find("div.error");
        this.scrollTo = form_group.parents("div.section");

        this.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
            error.hide();
        };

        input.focus(this.clearError);
        input.focusout(this.validate);
    }

    function DifficultyValidator() {
        var that = this;
        var form_group = form.find("div.form-group.difficulty");
        var select = form_group.find("select[name='difficulty']");
        var error = form_group.find("div.error");
        this.scrollTo = form_group;

        this.validate = function() {
            var valid = select.find("option:selected").val() !== '';
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
            error.hide();
        };

        select.change(this.clearError);
    }

    function AudienceValidator() {
        var that = this;
        var form_group = form.find("div.form-group.audiences");
        var select = form_group.find("select[name='audiences']");
        var error = form_group.find("div.error");
        this.scrollTo = form_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
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
        var form_group = form.find("div.form-group.category, div.form-group.subcategories");
        var error = form_group.find("div.error");
        var category_inputs = form_group.find("input[type='radio']");
        var subcategory_buttons = form_group.find("button.subcategory");
        this.scrollTo = form_group;

        this.validate = function() {
            var category = category_inputs.filter(":checked").val();
            var valid = subcategory_buttons.is("." + category + ".btn-danger");
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
            error.hide();
        };

        category_inputs.click(this.clearError);
        subcategory_buttons.click(this.clearError);
    }

    function CountyValidator() {
        var that = this;
        var form_group = form.find("div.form-group.counties");
        var error = form_group.find("div.error");
        var select = form_group.find("select[name='counties']");
        this.scrollTo = form_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
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
        var form_group = form.find("div.form-group.municipalities");
        var error = form_group.find("div.error");
        var select = form_group.find("select[name='municipalities']");
        this.scrollTo = form_group;

        this.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
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
        var form_group = form.find("div.form-group.pub_date");
        var error = form_group.find("div.error");
        var date = form_group.find("div.date");
        var input = form_group.find("input[name='pub_date']");
        this.scrollTo = form_group;

        this.validate = function() {
            var valid = input.val().match(/^\d\d\.\d\d\.\d\d\d\d$/) !== null;
            if(!valid) {
                that.markError();
            }
            return valid;
        };

        this.markError = function() {
            form_group.addClass('has-error');
            error.show();
        };

        this.clearError = function() {
            form_group.removeClass('has-error');
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
            dates.find("div.date-root:not(.jq-hide)").each(function() {
                var view = $(this).data('view');

                var validators = [
                    new StartTimeValidator(view.root),
                    new EndTimeValidator(view.root),
                    new SignupStartValidator(view.root),
                    new SignupDeadlineValidator(view.root),
                    new SignupCancelDeadlineValidator(view.root),
                    new MeetingPlaceValidator(view.root),
                    new ContactValidator(view.root),
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

            var form_group = root.find("div.form-group.start_date");
            var error = form_group.find("div.error");
            var date_control = form_group.find("div.date");
            var date_input = form_group.find("input[name='start_date']");
            var time_input = form_group.find("input[name='start_time']");
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
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        // End datetime format
        function EndTimeValidator(root) {

            var form_group = root.find("div.form-group.end_date");
            var error = form_group.find("div.error");
            var date_control = form_group.find("div.date");
            var date_input = form_group.find("input[name='end_date']");
            var time_input = form_group.find("input[name='end_time']");
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
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        // End datetime format
        function SignupStartValidator(root) {

            var form_group_signup = root.find("div.form-group.signup");
            var form_group = root.find("div.form-group.signup_start");
            var error = form_group.find("div.error");
            var signup_start = form_group.find("div.date");
            var signup_start_input = form_group.find("input[name='signup_start']");
            this.scrollTo = root;

            this.validate = function() {

                if(form_group_signup.find("input:checked").is("[value='none']")) {
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
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        // End datetime format
        function SignupDeadlineValidator(root) {

            var form_group_signup = root.find("div.form-group.signup");
            var form_group = root.find("div.form-group.signup_deadline");
            var error = form_group.find("div.error");
            var signup_deadline_until_start = form_group.find("input[name='signup_deadline_until_start']");
            var signup_deadline = form_group.find("div.date");
            var signup_deadline_input = form_group.find("input[name='signup_deadline']");
            this.scrollTo = root;

            this.validate = function() {

                if(form_group_signup.find("input:checked").is("[value='none']")) {
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
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        // End datetime format
        function SignupCancelDeadlineValidator(root) {

            var form_group_signup = root.find("div.form-group.signup");
            var form_group = root.find("div.form-group.signup_cancel_deadline");
            var error = form_group.find("div.error");
            var signup_cancel_deadline_until_start = form_group.find("input[name='signup_cancel_deadline_until_start']");
            var signup_cancel_deadline = form_group.find("div.date");
            var signup_cancel_deadline_input = form_group.find("input[name='signup_cancel_deadline']");
            this.scrollTo = root;

            this.validate = function() {

                if(form_group_signup.find("input:checked").is("[value='none']")) {
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
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        function MeetingPlaceValidator(root) {

            var form_group = root.find("div.form-group.meeting_place");
            var input = form_group.find("textarea[name='meeting_place']");
            var error = form_group.find("div.error");
            this.scrollTo = root;

            this.validate = function() {
                var valid = input.val().trim() !== "";
                if(!valid) {
                    // Not valid, but it's not required, so ask the user if they're sure
                    // TODO: this will ask multiple times if there are multiple dates without
                    // this value - consider handling that
                    if(confirm("Du har ikke beskrevet oppmøtested for en av turavgangene. Vil du virkelig fortsette uten å legge inn oppmøtested?")) {
                        // User accepts, continue as if it's valid
                        valid = true;
                    }
                }
                if(!valid) {
                    markError();
                }
                return valid;
            };

            input.focus(clearError);

            function markError() {
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

        function ContactValidator(root) {

            var form_group = root.find("div.form-group.contact_type");
            var error = form_group.find("div.error");
            var custom_group = root.find("div.contact-custom");
            var radios = form_group.find("input[type='radio']");
            var name_input = custom_group.find("input[name='contact_custom_name']");
            var phone_input = custom_group.find("input[name='contact_custom_phone']");
            var email_input = custom_group.find("input[name='contact_custom_email']");
            this.scrollTo = form_group;

            this.validate = function() {
                if(!radios.filter(":checked").is("[value='custom']")) {
                    return true;
                }

                var name_valid = name_input.val().trim() !== "";
                var phone_valid = name_input.val().trim() !== "";
                var email_valid = name_input.val().trim() !== "";
                var valid = name_valid || phone_valid || email_valid;

                if(!valid) {
                    markError();
                }
                return valid;
            };

            radios.change(clearError);
            name_input.focus(clearError);
            phone_input.focus(clearError);
            email_input.focus(clearError);

            function markError() {
                form_group.addClass('has-error');
                error.show();
            }

            function clearError() {
                form_group.removeClass('has-error');
                error.hide();
            }
        }

    }

});
