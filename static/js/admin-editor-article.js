$(document).ready(function() {

  $(".static").hover(function() {
    $(this).addClass('static-hover');
  }, function() {
    $(this).removeClass('static-hover');
  });

  $(".changeable").hover(function() {
    $(this).addClass('hover');
  }, function() {
    $(this).removeClass('hover');
  }).click(function() {
    $(this).removeClass('hover');
  });

  $(".editable").attr('contenteditable', 'true');

});
