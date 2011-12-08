$(document).ready(function() {

    $("#forediting").children().each(function() {
        $(this).attr('contenteditable', 'true');
    });

});
