$(document).ready(function() {
    var register = $("div.turlederregister-edit");
    var table = register.find("table.edit");
    var active_associations = register.find("select[name='active_associations']");
    var active_associations_all_checkbox = register.find("input[name='active_associations_all_checkbox']");
    var form_active_associations = register.find("form.active-associations");
    var active_associations_all_form = form_active_associations.find("input[name='active_associations_all']");

    register.find("div.role").each(function() {

        var status_empty = $(this).find("p.status-empty");
        var status_exists = $(this).find("p.status-exists");
        var create = status_empty.find("a.create");
        var edit = status_exists.find("a.edit");
        var remove = status_exists.find("a.remove");
        var form = $(this).find("form.edit-certificate");

        create.click(function() {
            status_empty.hide();
            status_exists.hide();
            form.slideDown();
        });

        edit.click(function() {
            status_empty.hide();
            status_exists.hide();
            form.slideDown();
        });

        remove.click(function(e) {
            if(!confirm("Helt sikker på at du vil slette " + $(this).attr('data-certificate-name') + "-sertifikatet for denne personen?")) {
                e.preventDefault();
            }
        });

        $(this).find("div.input-append.date").datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            autoclose: true,
            forceParse: false
        });

        form.submit(function(e) {
            if($(this).find("select[name='association_approved'] option:selected").val() === '') {
                alert("Du må angi hvilken forening som godkjente turledersertifikatet.");
                e.preventDefault();
            }

            if(!Validator.check['date']($(this).find("input[name='date_start']").val(), true)) {
                alert("Vennligst oppgi en gyldig dato for når sertifikatet ble tilordnet.");
                e.preventDefault();
            }

            if(!Validator.check['date']($(this).find("input[name='date_end']").val(), true)) {
                alert("Vennligst oppgi en gyldig dato for når sertifikatet utløper.");
                e.preventDefault();
            }
        });

    });

    form_active_associations.submit(function(e) {
        var active_association_ids = [];
        active_associations.find("option:selected").each(function() {
            active_association_ids.push($(this).val());
        });
        form_active_associations.find("input[name='active_association_ids']").val(JSON.stringify(active_association_ids));
        active_associations_all_form.val(JSON.stringify(active_associations_all_checkbox.is(":checked")));
    });

    active_associations_all_checkbox.change(function() {
        var disabled = active_associations_all_checkbox.is(":checked");
        active_associations.prop("disabled", disabled);
        active_associations.find("option").prop("disabled", disabled);
        active_associations.trigger('liszt:updated');
    });
    active_associations_all_checkbox.change();

});
