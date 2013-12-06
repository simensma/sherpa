$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");

    (function(AktivitetValidator, $, undefined ) {

        AktivitetValidator.validate = function() {

            var valid = true;
            var scrollTo;

            if(!TitleValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || TitleValidator.scrollTo;
            }

            if(!DescriptionValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || DescriptionValidator.scrollTo;
            }

            if(!DifficultyValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || DifficultyValidator.scrollTo;
            }

            if(!AudienceValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || AudienceValidator.scrollTo;
            }

            if(!CategoryValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || CategoryValidator.scrollTo;
            }

            if(!CountyValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || CountyValidator.scrollTo;
            }

            if(!MunicipalityValidator.validate()) {
                valid = false;
                scrollTo = scrollTo || MunicipalityValidator.scrollTo;
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

    // Require title
    (function(TitleValidator, $, undefined ) {

        var control_group = form.find("div.control-group.title");
        var input = control_group.find("input[name='title']");
        var error = control_group.find("div.error");

        TitleValidator.scrollTo = control_group.parents("div.section").offset().top;

        TitleValidator.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                markError();
            }
            return valid;
        };

        input.focus(clearError);
        input.focusout(TitleValidator.validate);

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.TitleValidator = window.TitleValidator || {}, jQuery ));

    // Require description
    (function(DescriptionValidator, $, undefined ) {

        var control_group = form.find("div.control-group.description");
        var input = control_group.find("textarea[name='description']");
        var error = control_group.find("div.error");

        DescriptionValidator.scrollTo = control_group.parents("div.section").offset().top;

        DescriptionValidator.validate = function() {
            var valid = input.val().trim() !== '';
            if(!valid) {
                markError();
            }
            return valid;
        };

        input.focus(clearError);
        input.focusout(DescriptionValidator.validate);

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.DescriptionValidator = window.DescriptionValidator || {}, jQuery ));

    // Require difficulty
    (function(DifficultyValidator, $, undefined ) {

        var control_group = form.find("div.control-group.difficulty");
        var select = control_group.find("select[name='difficulty']");
        var error = control_group.find("div.error");

        DifficultyValidator.scrollTo = control_group.offset().top;

        DifficultyValidator.validate = function() {
            var valid = select.find("option:selected").val() !== '';
            if(!valid) {
                markError();
            }
            return valid;
        };

        select.change(clearError);

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.DifficultyValidator = window.DifficultyValidator || {}, jQuery ));

    // Require at least one audience
    (function(AudienceValidator, $, undefined ) {

        var control_group = form.find("div.control-group.audiences");
        var select = control_group.find("select[name='audiences']");
        var error = control_group.find("div.error");

        AudienceValidator.scrollTo = control_group.offset().top;

        AudienceValidator.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                markError();
            }
            return valid;
        };

        select.change(function() {
            if(AudienceValidator.validate()) {
                clearError();
            }
        });

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.AudienceValidator = window.AudienceValidator || {}, jQuery ));

    // Require at least one predefined category
    (function(CategoryValidator, $, undefined ) {

        var control_group = form.find("div.control-group.category, div.control-group.subcategories");
        var error = control_group.find("div.error");
        var category_buttons = control_group.find("button[data-category]");
        var subcategory_buttons = control_group.find("button.subcategory");

        CategoryValidator.scrollTo = control_group.offset().top;

        CategoryValidator.validate = function() {
            var category = category_buttons.filter(".active").attr('data-category');
            var valid = subcategory_buttons.is("." + category + ".btn-danger");
            if(!valid) {
                markError();
            }
            return valid;
        };

        category_buttons.click(clearError);
        subcategory_buttons.click(clearError);

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.CategoryValidator = window.CategoryValidator || {}, jQuery ));

    // Require at least one county
    (function(CountyValidator, $, undefined ) {

        var control_group = form.find("div.control-group.counties");
        var error = control_group.find("div.error");
        var select = control_group.find("select[name='counties']");

        CountyValidator.scrollTo = control_group.offset().top;

        CountyValidator.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                markError();
            }
            return valid;
        };

        select.change(function() {
            if(CountyValidator.validate()) {
                clearError();
            }
        });

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.CountyValidator = window.CountyValidator || {}, jQuery ));

    // Require at least one municipality
    (function(MunicipalityValidator, $, undefined ) {

        var control_group = form.find("div.control-group.municipalities");
        var error = control_group.find("div.error");
        var select = control_group.find("select[name='municipalities']");

        MunicipalityValidator.scrollTo = control_group.offset().top;

        MunicipalityValidator.validate = function() {
            var valid = select.find("option:selected").length !== 0;
            if(!valid) {
                markError();
            }
            return valid;
        };

        select.change(function() {
            if(MunicipalityValidator.validate()) {
                clearError();
            }
        });

        function markError() {
            control_group.addClass('error');
            error.show();
        }

        function clearError() {
            control_group.removeClass('error');
            error.hide();
        }

    }(window.MunicipalityValidator = window.MunicipalityValidator || {}, jQuery ));

});
