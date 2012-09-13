$(document).ready(function() {
    $("form#gift").hide();
    $("div.gift-choice").click(function() {
        $("div.gift-choice").removeClass('active');
        $(this).addClass('active');
        $("p.type-display span").hide();
        $("p.type-display span." + $(this).attr('data-name')).show();
        $("form#gift").show();
    });

    $("form#gift input.zipcode").keyup(function() {
        var self = $(this);
        if(self.val().match(/^\d{4}$/)) {
            self.siblings("img.ajaxloader").show();
            $.ajaxQueue({
                url: '/postnummer/' + encodeURIComponent(self.val()) + '/',
                type: 'POST'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.location != undefined) {
                    self.siblings("input.city").val(result.location);
                    self.parents("div.control-group.zipcode").removeClass('error').addClass('success');
                } else if(result.error == "does_not_exist") {
                    self.siblings("input.city").val("Ukjent postnummer");
                    self.parents("div.control-group.zipcode").removeClass('success').addClass('error');
                }
            }).fail(function(result) {
                self.siblings("input.city").val("Teknisk feil");
                self.parents("div.control-group.zipcode").removeClass('success').addClass('error');
            }).always(function(result) {
                self.siblings("img.ajaxloader").hide();
            });
        } else {
            self.siblings("input.city").val("");
        }
    });
});
