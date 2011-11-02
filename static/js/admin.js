$(document).ready(function() {
  $("form#new_page_form").animate({height: "toggle"}, 0);
});

$(function() {
  $("a#new_page").click(function(event) {
    $("form#new_page_form").animate({height: "toggle"}, 400);
  });
});
