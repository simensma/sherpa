$(function() {

    $("div.image-archive-quicksearch select").select2();

    $("select[name='user-images']").on('change', function (e) {
        var selected = $(this).find("option:selected");
        var id = e.val;
        var url = selected.attr('data-href').replace(/0\//, id + '/');
        window.location = url;
    });

});
