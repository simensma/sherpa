$(function() {

    var wrapper = $("div.setup-site");

    var site_type_wrapper = wrapper.find("div.form-group.type");
    var site_type_buttons = site_type_wrapper.find("input[name='type']");

    var title_wrapper = wrapper.find("div.form-group.title");

    var domain_wrapper = wrapper.find("div.form-group.domain");
    var domain = domain_wrapper.find("input[name='domain']");
    var domain_type = domain_wrapper.find("input[name='domain-type']");
    var subdomain_tail = domain_wrapper.find("span.subdomain-tail");
    var submit = domain_wrapper.find("button[type='submit']");

    site_type_buttons.change(function() {
        if(site_type_buttons.filter(":checked").is("[value='kampanje']")) {
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

    submit.click(function(e) {
        if(domain.val().trim() === 'forening' || domain.val().trim() === '') {
            alert(submit.attr('data-enter-domain-warning'));
            e.preventDefault();
        }
    });

});
