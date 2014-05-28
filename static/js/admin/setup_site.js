$(function() {

    var wrapper = $("div.setup-site");
    var domain = wrapper.find("input[name='domain']");
    var submit = wrapper.find("button[type='submit']");

    submit.click(function(e) {
        if(domain.val().trim() === 'forening' || domain.val().trim() === '') {
            alert(submit.attr('data-enter-domain-warning'));
            e.preventDefault();
        }
    });

});
