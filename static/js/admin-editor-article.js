$(window).load(function() {
  // Don't set contenteditable until the entire window is loaded
  $(".editable").attr('contenteditable', 'true');
});

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

  /* Saving document */

  $("#toolbar a.save").click(function() {
    $("article .editable").removeAttr('contenteditable');
    var contents = [];
    $("div.content").each(function() {
      var content = {
        id: $(this).attr('data-id'),
        content: $(this).html()
      }
      contents = contents.concat([content]);
    });

    $.ajax({
      url: '/sherpa/artikler/oppdater/' + $("article").attr('data-id') + '/',
      type: 'POST',
      data: "contents=" + encodeURIComponent(JSON.stringify(contents))
    }).done(function(result) {
      // Todo
    }).fail(function(result) {
      // Todo
    }).always(function(result) {
      // Todo
    });
  });

});

/* Figures that "span" is 8 for a class list of e.g. "offset4 span8" */
function parseColumn(classList, name) {
  for(i=0; i<classList.length; i++) {
    if(classList[i].substring(0, classList[i].length-1) == name) {
      return classList[i].substring(classList[i].length-1)
    }
  }
}
