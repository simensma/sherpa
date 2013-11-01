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

    // Turledere

    var turleder_list = this.edit_root.find("ul.turleder-list");
    var turleder_search = this.edit_root.find("div.turleder-search");
    var turleder_table = turleder_search.find("table.search-results");
    var turleder_input = turleder_search.find("input[name='turleder-search']");
    var turleder_button = turleder_search.find("button.turleder-search");

    var turleder_loader = turleder_table.find("tr.loader");
    var turleder_no_hits = turleder_table.find("tr.no-hits");
    var turleder_short_query = turleder_table.find("tr.short_query");
    var turleder_error = turleder_table.find("tr.technical-error");
    var turleder_max_hits_exceeded = turleder_table.find("tr.max-hits-exceeded");
    var turleder_result_mirror = turleder_no_hits.find("span.result-mirror");

    turleder_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            turleder_button.click();
        }
    });

    turleder_button.click(function() {
        turleder_input.prop('disabled', true);
        turleder_button.prop('disabled', true);
        turleder_table.slideDown();
        turleder_loader.show();
        turleder_no_hits.hide();
        turleder_short_query.hide();
        turleder_error.hide();
        turleder_max_hits_exceeded.hide();
        turleder_table.find("tr.result").remove();

        var query = turleder_input.val();
        if(query.length < Turistforeningen.admin_user_search_char_length) {
            turleder_input.prop('disabled', false);
            turleder_button.prop('disabled', false);
            turleder_short_query.show();
            turleder_loader.hide();
            return;
        }

        $.ajaxQueue({
            url: turleder_table.attr('data-search-url'),
            data: { q: query }
        }).done(function(result) {
            result = JSON.parse(result);
            turleder_table.find("tr.result").remove();
            if(result.results.trim() === '') {
                turleder_result_mirror.text(query);
                turleder_no_hits.show();
            } else {
                turleder_table.append(result.results);
                if(result.max_hits_exceeded) {
                    max_hits_exceeded.show();
                }
                turleder_table.find("tr.result a.assign-turleder").click(function() {
                    turleder_table.hide();
                    var new_element = turleder_list.find("li.hide").clone();
                    new_element.removeClass('hide');
                    var content = $(this).attr('data-name') + ' (' + $(this).attr('data-memberid') + ')';
                    new_element.find("span.content").text(content);
                    new_element.attr('data-id', $(this).attr('data-id'));
                    new_element.attr('data-type', $(this).attr('data-type'));
                    new_element.appendTo(turleder_list);
                });
            }
        }).fail(function(result) {
            turleder_table.find("tr.result").remove();
            turleder_error.show();
        }).always(function(result) {
            turleder_loader.hide();
            turleder_input.prop('disabled', false);
            turleder_button.prop('disabled', false);
        });
    });

    $(document).on('click', turleder_list.selector + ' a.remove-turleder', function() {
        $(this).parents("li").remove();
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
    var turledere = {
        users: [],
        actors: []
    };
    this.root.find("ul.turleder-list li:not(.hide)").each(function() {
        turledere[$(this).attr('data-type') + 's'].push($(this).attr('data-id'));
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
        turledere: turledere
    };
};
