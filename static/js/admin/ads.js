$(function() {

    var ads = $("div.advertisement-management");

    var form_placement = ads.find("form.placement");
    var table_placements_time = ads.find("table.placements.time");
    var table_placements_view = ads.find("table.placements.view");
    var table_ads = ads.find("table.ads");
    var modal_placement_time = ads.find("div.modal.placement.time");
    var modal_placement_view = ads.find("div.modal.placement.view");
    var modal_ad_file = ads.find("div.modal.ad.file");
    var modal_ad_adform_script = ads.find("div.modal.ad.adform-script");

    ads.find("a.toggle-old-placements").click(function() {
        $(this).parents("tr").siblings("tr.inactive, tr.old").toggle();
    });

    function updateCheck() {
        if(form_placement.find(".time input[name='adplacement_type']:checked").length > 0) {
            form_placement.find(".time input[name='start_date'], .time input[name='end_date']").prop('disabled', false);
            form_placement.find(".view input[name='view_limit']").val('').prop('disabled', true);
        } else if(form_placement.find(".view input[name='adplacement_type']:checked").length > 0) {
            form_placement.find(".time input[name='start_date'], .time input[name='end_date']").val('').prop('disabled', true);
            form_placement.find(".view input[name='view_limit']").prop('disabled', false);
        }
    }

    form_placement.find("input[name='adplacement_type']").click(updateCheck);
    form_placement.find(".time input[name='adplacement_type']").click();
    updateCheck();

    var dp_options = {
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    };
    form_placement.find("div.date").datepicker(dp_options);
    ads.find("div.placement-dialog.time form div.date").datepicker(dp_options);

    table_placements_time.find("tr.placement").click(function() {
        var form = modal_placement_time.find("form");
        form.find("input[name='id']").val($(this).attr('data-id'));
        form.find("select[name='ad'] option[value='" + $(this).attr('data-ad') + "']").prop('selected', true);
        form.find("select[name='ad']").trigger('liszt:updated');
        form.find("input[name='start_date']").val($(this).attr('data-start-date'));
        form.find("input[name='end_date']").val($(this).attr('data-end-date'));
        // The bootstrap-datepicker 'update' method doesn't work, see:
        // https://github.com/eternicode/bootstrap-datepicker/issues/240
        // Just remove and recreate it for now.
        form.find("div.date").datepicker('remove').datepicker(dp_options);
        modal_placement_time.modal();
    });

    table_placements_view.find("tr.placement").click(function() {
        var form = modal_placement_view.find("form");
        form.find("input[name='id']").val($(this).attr('data-id'));
        form.find("select[name='ad'] option[value='" + $(this).attr('data-ad') + "']").prop('selected', true);
        form.find("input[name='view_limit']").val($(this).attr('data-view-limit'));
        modal_placement_view.modal();
    });

    table_ads.find("td.ad").click(function() {
        if($(this).is(".file")) {
            var form = modal_ad_file.find("form");
            form.find("input[name='id']").val($(this).attr('data-id'));
            form.find("input[name='name']").val($(this).attr('data-name'));
            form.find("input[name='destination']").val($(this).attr('data-destination'));
            form.find("input[name='viewcounter']").val($(this).attr('data-viewcounter'));
            form.find("input[name='width']").val($(this).attr('data-width'));
            form.find("input[name='height']").val($(this).attr('data-height'));
            modal_ad_file.modal();
        } else {
            var form = modal_ad_adform_script.find("form");
            form.find("input[name='id']").val($(this).attr('data-id'));
            form.find("input[name='name']").val($(this).attr('data-name'));
            form.find("textarea[name='script']").val($(this).attr('data-script'));
            modal_ad_adform_script.modal();
        }
    });
});
