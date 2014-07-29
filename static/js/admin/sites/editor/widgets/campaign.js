$(function() {

    var $campaigns;
    var $campaign_template;

    var $add_campaign_button;
    var $hide_when_expired;

    WidgetEditor.listen({
        widget_name: 'campaign',

        init: function($editor) {
            $campaigns = $editor.find('[data-dnt-container="campaigns"]');
            $campaign_template = $editor.find('[data-dnt-template="campaign"]');
            $add_campaign_button = $editor.find('button[data-dnt-toggle="add-campaign"]');
            $hide_when_expired = $editor.find('input[name="hide-when-expired"]');
            $display_core_menu = $editor.find('input[name="display-core-menu"]');
            $add_campaign_button.click(addCampaign);
        },

        onNew: function($editor) {
            $campaigns.empty();
            addCampaign();
            $hide_when_expired.filter('[value="true"]').prop('checked', true);
            $display_core_menu.prop('checked', false);
        },

        onEdit: function($editor, widget_content) {
            $campaigns.empty();
            for(var i=0; i<widget_content.campaigns.length; i++) {
                addCampaign();
                var $campaign = $campaigns.children().last();
                var campaign = $campaign.find('select[name="campaign"]');
                campaign.find('option[value="' + widget_content.campaigns[i].campaign_id + '"]').prop('selected', true);
                campaign.trigger("liszt:updated"); // Update chosen
                $campaign.find('input[name="start-date"]').val(widget_content.campaigns[i].start_date);
                $campaign.find('input[name="stop-date"]').val(widget_content.campaigns[i].stop_date);
            }

            if(widget_content.hide_when_expired) {
                $hide_when_expired.filter('[value="true"]').prop('checked', true);
            } else {
                $hide_when_expired.filter('[value="false"]').prop('checked', true);
            }

            $display_core_menu.prop('checked', widget_content.display_core_menu);
        },

        onSave: function($editor) {
            var campaigns = [];
            var break_ = false;
            $campaigns.children().each(function() {
                var campaign_id = $(this).find('select[name="campaign"] option:selected').val();
                var start_date = $(this).find('input[name="start-date"]').val();
                var stop_date = $(this).find('input[name="stop-date"]').val();

                if(campaign_id === '') {
                    return $(this);
                }
                var date_format = /^\d\d\.\d\d\.\d\d\d\d$/;
                if(start_date.match(date_format) === null || stop_date.match(date_format === null)) {
                    alert($campaigns.attr('data-dnt-invalid-date-format'));
                    break_ = true;
                }

                campaigns.push({
                    campaign_id: campaign_id,
                    start_date: start_date,
                    stop_date: stop_date,
                });

            });

            if(break_) {
                return false;
            }

            if(campaigns.length === 0) {
                alert($campaigns.attr('data-dnt-missing-campaign'));
                return false;
            }

            var hide_when_expired = $hide_when_expired.filter(':checked').val() === 'true';

            WidgetEditor.saveWidget({
                widget: 'campaign',
                campaigns: campaigns,
                hide_when_expired: hide_when_expired,
                display_core_menu: $display_core_menu.prop('checked'),
            });
            return true;
        }
    });

    function addCampaign() {
        var $campaign = $campaign_template.clone();
        $campaign.removeAttr('data-dnt-template');
        $campaign.appendTo($campaigns);

        $campaign.find('select[name="campaign"]').chosen();
        $campaign.find('[data-dnt-container="datepicker"]').datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            autoclose: true,
            forceParse: false
        });

        $campaign.find('button[data-dnt-toggle="remove-campaign"]').click(function() {
            $campaign.remove();
        });

        $campaign.show();
    }

});
