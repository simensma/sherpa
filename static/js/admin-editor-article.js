$(document).ready(function() {

  $(".static").hover(function() {
    $(this).addClass('static-hover');
  }, function() {
    $(this).removeClass('static-hover');
  });

  $("img.changeable").hover(function() {
    $(this).addClass('hover');
  }, function() {
    $(this).removeClass('hover');
  }).click(function() {
    $(this).removeClass('hover');
    var src = prompt("URL?");
    if(src !== null && src !== undefined) {
      $(this).attr('src', src);
    }
  });

  $(".editable").attr('contenteditable', 'true');

});
