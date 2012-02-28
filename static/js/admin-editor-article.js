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

  /* Saving document */

  $("#toolbar a.save").click(function() {
    $("article .editable").removeAttr('contenteditable');
    var data = {
      id: $("article").attr('data-id'),
      rows: []
    }
    $("article div.row").each(function() {
      var row = {
        columns: []
      }
      $(this).children().each(function() {
        var column = {
          id: $(this).attr('data-id'),
          content: $(this).html(),
          span: parseColumn($(this).attr('class').split(' '), 'span'),
          offset: parseColumn($(this).attr('class').split(' '), 'offset')
        }
        row.columns = row.columns.concat([column])
      });
      data.rows = data.rows.concat([row]);
    });

    $.ajax({
      url: '/sherpa/artikler/oppdater/' + data.id + '/',
      type: 'POST',
      data: "template=" + encodeURIComponent($("article").attr('data-template'))
        + "&json=" + encodeURIComponent(JSON.stringify(data))
    }).done(function(result) {
      // Todo: State change!
      // Change article 'data-template' attr, add id-attrs to all elements (or just redirect)
      setSaveStatus('saved');
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
