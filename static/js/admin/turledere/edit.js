$(document).ready(function() {
    var register = $("div.turlederregister");
    var table = register.find("table.edit");
    var active_associations = register.find("select[name='active_associations']");
    var active_associations_all_checkbox = register.find("input[name='active_associations_all_checkbox']");
    var form = register.find("form.save");
    var active_associations_all_form = form.find("input[name='active_associations_all']");

    function addHandlers(item) {
        item.find("select[name='role']").chosen({disable_search: true});
        item.find("select[name='association_approved']").chosen();
        item.find("div.input-append.date").datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            autoclose: true,
            language: 'nb'
        });
    }
    addHandlers(register.find("tr[data-turleder]"));

    table.find("tr.add a").click(function() {
        var new_turleder = table.find("tr.new");
        var clone = new_turleder.clone();
        clone.removeClass('hide new').insertBefore(new_turleder).attr('data-turleder', '');
        addHandlers(clone);
    });

    $(document).on('click', table.selector + ' td.delete a', function() {
        $(this).parents("tr").remove();
    });

    form.submit(function(e) {
        var active_association_ids = [];
        active_associations.find("option:selected").each(function() {
            active_association_ids.push($(this).val());
        });
        form.find("input[name='active_association_ids']").val(JSON.stringify(active_association_ids));
        active_associations_all_form.val(JSON.stringify(active_associations_all_checkbox.is(":checked")));
        var turledere = [];
        table.find("tr[data-turleder]").each(function() {
            var role = $(this).find("select[name='role'] option:selected").val();
            var association_approved = $(this).find("select[name='association_approved'] option:selected").val();
            var date_start = $(this).find("input[name='date_start']").val();
            var date_end = $(this).find("input[name='date_end']").val();

            if(role === '') {
                alert("Du må angi turlederrollen.");
                e.preventDefault();
            }

            if(association_approved === '') {
                alert("Du må angi hvilken forening som godkjente turlederen.");
                e.preventDefault();
            }

            turledere.push({
                id: $(this).attr('data-turleder'),
                role: role,
                association_approved: association_approved,
                date_start: date_start,
                date_end: date_end
            });
        });
        form.find("input[name='turledere']").val(JSON.stringify(turledere));
    });

    active_associations_all_checkbox.change(function() {
        var disabled = active_associations_all_checkbox.is(":checked");
        active_associations.prop("disabled", disabled);
        active_associations.find("option").prop("disabled", disabled);
        active_associations.trigger('liszt:updated');
    });
    active_associations_all_checkbox.change();

});
