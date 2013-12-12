var AktiviteterDatesView = function(opts) {
    var that = this;

    this.root = opts.root;

    this.view_root = this.root.find("div.date-view");
    this.edit_root = this.root.find("div.date-edit");
    this.view_ajaxloader = this.view_root.find("img.ajaxloader");
    this.view_date_display = this.view_root.find("div.date-display");
    this.view_fail = this.view_root.find("div.date-display-fail");

    this.start_date = this.root.find("div.control-group.start_date div.date");
    this.start_time = this.root.find("input[name='start_time']");
    this.end_date = this.root.find("div.control-group.end_date div.date");
    this.end_time = this.root.find("input[name='end_time']");
    this.signup_start = this.root.find("div.control-group.signup_start div.date");
    this.signup_start_input = this.signup_start.find("input");
    this.signup_deadline = this.root.find("div.control-group.signup_deadline div.date");
    this.signup_deadline_input = this.signup_deadline.find("input");
    this.signup_deadline_until_start = this.root.find("input[name='signup_deadline_until_start']");
    this.signup_cancel_deadline = this.root.find("div.control-group.signup_cancel_deadline div.date");
    this.signup_cancel_deadline_input = this.signup_cancel_deadline.find("input");
    this.signup_cancel_deadline_until_start = this.root.find("input[name='signup_cancel_deadline_until_start']");

    var trigger_edit = this.view_root.find("a.trigger-date-editor");
    this.enrollment_inputs = this.edit_root.find("input[name^='enrollment']");
    var enrollment_group = this.edit_root.find("div.enrollment-group");
    this.contact_inputs = this.edit_root.find("input[name^='contact']");
    var contact_custom = this.edit_root.find("div.contact-custom");

    trigger_edit.click(function() {
        if(that.edit_root.is(":hidden")) {
            that.edit();
        } else {
            that.view();
        }
    });

    // All dateinputs

    this.edit_root.find("div.input-append.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    });

    // Hide/show signup options

    this.enrollment_inputs.change(function() {
        var val = that.enrollment_inputs.filter(":checked").val();

        if(val === 'minside') {
            enrollment_group.slideDown();
        } else if(val === 'simple') {
            enrollment_group.slideDown();
        } else if(val === 'none') {
            enrollment_group.slideUp();
        }
    });

    // Don't cross the start- and enddates
    // Instead of limiting the options, we'll just move the *other* date
    // when the one changing crosses it.

    this.start_date.on('changeDate', function() {
        var start_date = $(this).datepicker('getDate');
        if(that.end_date.datepicker('getDate') < start_date) {
            that.end_date.datepicker('setDate', start_date);
            that.end_date.datepicker('update');
        }

        // Limit the signup and signup-cancel dates
        if(!that.signup_start_input.prop("disabled") && that.signup_start.datepicker('getDate') > start_date) {
            that.signup_start.datepicker('setDate', start_date);
        }
        if(!that.signup_deadline_input.prop("disabled") && that.signup_deadline.datepicker('getDate') > start_date) {
            that.signup_deadline.datepicker('setDate', start_date);
        }
        if(!that.signup_cancel_deadline_input.prop("disabled") && that.signup_cancel_deadline.datepicker('getDate') > start_date) {
            that.signup_cancel_deadline.datepicker('setDate', start_date);
        }
        that.signup_start.datepicker('setEndDate', start_date);
        that.signup_deadline.datepicker('setEndDate', start_date);
        that.signup_cancel_deadline.datepicker('setEndDate', start_date);
        that.updateView();
    });

    this.end_date.on('changeDate', function() {
        var end_date = $(this).datepicker('getDate');
        if(that.start_date.datepicker('getDate') > end_date) {
            that.start_date.datepicker('setDate', end_date);
            that.start_date.datepicker('update');
        }
        that.updateView();
    });

    // Disable signup date inputs if until-start checkbox is checked

    this.signup_deadline_until_start.change(function() {
        if($(this).is(":checked")) {
            that.signup_deadline_input.prop('disabled', true);
            that.signup_deadline_input.attr('data-default-date', that.signup_deadline_input.val());
            that.signup_deadline_input.val('');
        } else {
            that.signup_deadline_input.prop('disabled', false);
            that.signup_deadline_input.val(that.signup_deadline_input.attr('data-default-date'));
        }
    });

    this.signup_cancel_deadline_until_start.change(function() {
        if($(this).is(":checked")) {
            that.signup_cancel_deadline_input.prop('disabled', true);
            that.signup_cancel_deadline_input.attr('data-default-date', that.signup_cancel_deadline_input.val());
            that.signup_cancel_deadline_input.val('');
        } else {
            that.signup_cancel_deadline_input.prop('disabled', false);
            that.signup_cancel_deadline_input.val(that.signup_cancel_deadline_input.attr('data-default-date'));
        }
    });

    // Hide/show custom contact information

    this.contact_inputs.change(function() {
        var val = that.contact_inputs.filter(":checked").val();

        if(val === 'arrangør') {
            contact_custom.slideUp();
        } else if(val === 'turleder') {
            contact_custom.slideUp();
        } else if(val === 'custom') {
            contact_custom.slideDown();
        }
    });

    // Turledere

    var turledere_add = this.edit_root.find("a.add-turledere");
    this.turleder_table = this.edit_root.find("table.turledere");

    turledere_add.click(function() {
        AdminAktivitetTurlederSearch.enable({
            callback: function(opts) {
                if(that.turleder_table.find("tr.display-result[data-id='" + opts.result_row.attr('data-id') + "']").length > 0) {
                    alert("Personen du valgte er allerede registrert som turleder på denne turen.");
                    return;
                }
                that.turleder_table.show();
                that.turleder_table.append(opts.result_row);
            }
        });
    });

    $(document).on('click', this.turleder_table.selector + ' a.remove-turleder', function() {
        var row = $(this).parents("tr.display-result");
        var turleder_table = $(this).parents("table.turledere");
        if(row.siblings("tr.display-result").length === 0) {
            turleder_table.hide();
        }
        row.remove();
    });

    $(document).on('click', this.turleder_table.selector + ' a.more', function() {
        $(this).hide();
        $(this).siblings("a.less").show();
        $(this).siblings("div.more").slideDown();
    });

    $(document).on('click', this.turleder_table.selector + ' a.less', function() {
        $(this).hide();
        $(this).siblings("a.more").show();
        $(this).siblings("div.more").slideUp();
    });

};

AktiviteterDatesView.prototype.view = function() {
    var that = this;
    this.updateView();
    this.edit_root.slideUp('slow');
};

AktiviteterDatesView.prototype.edit = function(opts) {
    opts = $.extend({
        instant: false
    }, opts);

    if(opts.instant) {
        this.edit_root.show();
    } else {
        this.edit_root.slideDown('slow');
    }
};

AktiviteterDatesView.prototype.updateView = function() {
    var that = this;
    var date_object = this.collectData();
    this.view_date_display.empty();
    this.view_ajaxloader.show();
    this.view_fail.hide();

    $.ajaxQueue({
        url: that.view_date_display.attr('data-date-preview-url'),
        data: { date: JSON.stringify(date_object) }
    }).done(function(result) {
        result = JSON.parse(result);
        var html = $($.parseHTML(result.html));
        that.view_date_display.append(html);
    }).fail(function(result) {
        that.view_fail.show();
    }).always(function(result) {
        that.view_ajaxloader.hide();
    });
};

AktiviteterDatesView.prototype.collectData = function() {
    var turledere = [];
    this.turleder_table.find("tr.display-result").each(function() {
        turledere.push($(this).attr('data-id'));
    });
    return {
        id: this.root.attr('data-date-id'),
        start_date: this.start_date.find("input").val(),
        start_time: this.start_time.val(),
        end_date: this.end_date.find("input").val(),
        end_time: this.end_time.val(),
        signup_type: this.root.find("input[name^='enrollment']:checked").val(),
        signup_start: this.signup_start_input.val(),
        signup_deadline: this.signup_deadline_input.val(),
        signup_deadline_until_start: this.signup_deadline_until_start.is(":checked"),
        signup_cancel_deadline: this.signup_cancel_deadline_input.val(),
        signup_cancel_deadline_until_start: this.signup_cancel_deadline_until_start.is(":checked"),
        turledere: turledere,
        meeting_place: this.root.find("textarea[name='meeting_place']").val(),
        contact_type: this.root.find("input[name^='contact_type']:checked").val(),
        contact_custom_name: this.root.find("input[name='contact_custom_name']").val(),
        contact_custom_phone: this.root.find("input[name='contact_custom_phone']").val(),
        contact_custom_email: this.root.find("input[name='contact_custom_email']").val()
    };
};
