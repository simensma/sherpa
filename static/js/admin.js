$(document).ready(function() {
  $("form#new_variant_form").animate({height: "toggle"}, 0);
});

$(function() {
  $("a#new_variant").click(function(event) {
    $("form#new_variant_form").animate({height: "toggle"}, 400);
  });
});
