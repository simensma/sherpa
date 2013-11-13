var AktiviteterDatesView = function(opts) {
    var that = this;

    this.root = opts.root;

    this.view_root = this.root.find("div.date-view");
    this.edit_root = this.root.find("div.date-edit");
    this.view_date_display = this.view_root.find("div.date-display");
    this.view_ajaxloader = this.view_root.find("img.ajaxloader");
    this.view_fail = this.view_root.find("div.fail");

    var action_view = this.edit_root.find("a.view-date");
    var action_edit = this.view_root.find("a.edit-date");
    this.enrollment_inputs = this.edit_root.find("input[name^='enrollment']");
    var enrollment_group = this.edit_root.find("div.enrollment-group");
    this.contact_inputs = this.edit_root.find("input[name^='contact']");
    var contact_custom = this.edit_root.find("div.contact-custom");

    action_view.click(function() {
        that.view();
    });

    action_edit.click(function() {
        that.edit();
    });

    // All dateinputs

    this.edit_root.find("div.input-append.date input").datepicker({
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
                that.turleder_table.append(opts.result_row);
            }
        });
    });

    $(document).on('click', this.turleder_table.selector + ' a.remove-turleder', function() {
        $(this).parents("tr.display-result").remove();
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
        // the root object should be a.edit-date - if that changes, this won't work
        html.click(function() {
            that.edit();
        });
    }).fail(function(result) {
        that.view_fail.show();
    }).always(function(result) {
        that.view_ajaxloader.hide();
    });

    var view_root = this.view_root;
    this.edit_root.slideUp('slow', function() {
        view_root.slideDown('fast');
    });
};

AktiviteterDatesView.prototype.edit = function() {
    var edit_root = this.edit_root;
    this.view_root.slideUp('fast', function() {
        edit_root.slideDown('slow');
    });
};

AktiviteterDatesView.prototype.collectData = function() {
    var turledere = [];
    this.turleder_table.find("tr.display-result").each(function() {
        turledere.push($(this).attr('data-id'));
    });
    return {
        id: this.root.attr('data-date-id'),
        start_date: this.root.find("input[name='start_date']").val(),
        start_time: this.root.find("input[name='start_time']").val(),
        end_date: this.root.find("input[name='end_date']").val(),
        end_time: this.root.find("input[name='end_time']").val(),
        signup_type: this.root.find("input[name^='enrollment']:checked").val(),
        signup_start: this.root.find("input[name='signup_start']").val(),
        signup_deadline: this.root.find("input[name='signup_deadline']").val(),
        signup_cancel_deadline: this.root.find("input[name='signup_cancel_deadline']").val(),
        turledere: turledere,
        meeting_place: this.root.find("textarea[name='meeting_place']").val(),
        contact_type: this.root.find("input[name^='contact_type']:checked").val(),
        contact_custom_name: this.root.find("input[name='contact_custom_name']").val(),
        contact_custom_phone: this.root.find("input[name='contact_custom_phone']").val(),
        contact_custom_email: this.root.find("input[name='contact_custom_email']").val()
    };
};
