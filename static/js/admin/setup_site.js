$(function() {

    var wrapper = $("div.setup-site");

    var site_type_wrapper = wrapper.find("div.form-group.type");
    var site_type_buttons = site_type_wrapper.find("input[name='type']");

    var title_wrapper = wrapper.find("div.form-group.title");

    var domain_wrapper = wrapper.find("div.form-group.domain");
    var domain = domain_wrapper.find("input[name='domain']");
    var domain_type = domain_wrapper.find("input[name='domain-type']");
    var subdomain_tail = domain_wrapper.find("span.subdomain-tail");

    var template_wrapper = wrapper.find("div.form-group.template");
    var template_input = template_wrapper.find("input[name='template']");
    var templates = template_wrapper.find("div.template-block");

    var submit = wrapper.find("button[type='submit']");

    site_type_buttons.change(function() {
        if(site_type_buttons.filter(":checked").is("[value='hytte']") || site_type_buttons.filter(":checked").is("[value='kampanje']")) {
            title_wrapper.slideDown('fast');
        } else {
            title_wrapper.slideUp('fast');
        }
    });

    domain_type.change(function() {
        if(domain_type.filter(":checked").is("[value='subdomain']")) {
            domain.removeClass('fqdn');
            subdomain_tail.show();
        } else {
            domain.addClass('fqdn');
            subdomain_tail.hide();
        }
    });

    templates.click(function() {
        templates.removeClass('active');
        $(this).addClass('active');
        template_input.val($(this).attr('data-template'));
    });

    submit.click(function(e) {
        if(site_type_buttons.filter(":checked").length === 0) {
            alert(submit.attr('data-choose-site-type-warning'));
            e.preventDefault();
            return;
        }
        if(domain.val().trim() === 'forening' || domain.val().trim() === '') {
            alert(submit.attr('data-enter-domain-warning'));
            e.preventDefault();
            return;
        }
        if(template_input.val().trim() === '') {
            alert(submit.attr('data-choose-template-warning'));
            e.preventDefault();
            return;
        }
    });

});
