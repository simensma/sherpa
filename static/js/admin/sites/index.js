$(function() {

    var site_admin = $('[data-dnt-container="site-admin-index"]');
    site_admin.find('.navigation-block[title]').tooltip();

    site_admin.find('[data-dnt-trigger="no-frontpage-warning"]').click(function() {
        alert($(this).attr('data-dnt-message'));
    });

});
