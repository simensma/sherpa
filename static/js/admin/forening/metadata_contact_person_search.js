// This module has a lot in common with js/admin/aktiviteter/edit/turleder_search.js and probably
// a few other similar modules too. Consider merging!

(function(AdminForeningContactPersonSearch, $, undefined ) {

    var that = this;

    $(function() {

        that.admin = $("div.foreningsadmin");
        that.search = admin.find("div.contact-person-search");

        that.table = search.find("table.search-results");
        that.search_input = search.find("input[name='search']");
        that.search_button = search.find("button.search");

        that.intro = that.table.find("tr.intro");
        that.loader = that.table.find("tr.loader");
        that.no_hits = that.table.find("tr.no-hits");
        that.short_query = that.table.find("tr.short_query");
        that.error = that.table.find("tr.technical-error");
        that.max_hits_exceeded = that.table.find("tr.max-hits-exceeded");
        that.result_mirror = that.no_hits.find("span.result-mirror");


        that.search_input.keyup(function(e) {
            if(e.which == 13) { // Enter
                that.search_button.click();
            }
        });

        that.search_button.click(function() {
            that.search_input.prop('disabled', true);
            that.search_button.prop('disabled', true);
            that.intro.hide();
            that.table.slideDown();
            that.loader.show();
            that.no_hits.hide();
            that.short_query.hide();
            that.error.hide();
            that.max_hits_exceeded.hide();
            that.table.find("tr.result").remove();

            var query = that.search_input.val();
            if(query.length < Turistforeningen.admin_user_search_char_length) {
                that.search_input.prop('disabled', false);
                that.search_button.prop('disabled', false);
                that.short_query.show();
                that.loader.hide();
                return;
            }

            $.ajaxQueue({
                url: that.table.attr('data-search-url'),
                data: { q: query }
            }).done(function(result) {
                result = JSON.parse(result);
                that.table.find("tr.result").remove();
                if(result.results.trim() === '') {
                    that.result_mirror.text(query);
                    that.no_hits.show();
                } else {
                    that.table.append(result.results);
                    if(result.max_hits_exceeded) {
                        that.max_hits_exceeded.show();
                    }
                    that.table.find("tr.result a.pick").click(function() {
                        that.callback({
                            result_row: $(this).parents("tr.result")
                        });
                        that.search.modal('hide');
                    });
                }
            }).fail(function(result) {
                that.table.find("tr.result").remove();
                that.error.show();
            }).always(function(result) {
                that.loader.hide();
                that.search_input.prop('disabled', false);
                that.search_button.prop('disabled', false);
            });
        });

    });

    AdminForeningContactPersonSearch.enable = function(opts) {
        that.callback = opts.callback;
        that.search.modal();
    };

}(window.AdminForeningContactPersonSearch = window.AdminForeningContactPersonSearch || {}, jQuery ));
