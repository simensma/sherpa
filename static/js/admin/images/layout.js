$(document).ready(function() {

    $("div.image-archive-quicksearch select").chosen();

    $("select[name='user-images']").change(function() {
        var selected = $(this).find("option:selected");
        var id = selected.val();
        var url = selected.attr('data-href').replace(/0\//, id + '/');
        window.location = url;
    });

});
