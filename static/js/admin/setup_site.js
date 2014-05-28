$(function() {

    var wrapper = $("div.setup-site");
    var step1 = wrapper.find("div.step1");
    var step2 = wrapper.find("div.step2");
    var domain = step2.find("input[name='domain']");
    var submit = step2.find("button[type='submit']");

    step1.find("label.btn").click(function() {
        step2.slideDown();
    });

    submit.click(function(e) {
        if(domain.val().trim() === 'forening' || domain.val().trim()) {
            alert(submit.attr('data-enter-domain-warning'));
            e.preventDefault();
        }
    });

});
