/* Look up zipcode objects */

LookupZipcode = function(zipcode, callback) {
    $.ajaxQueue({
        url: '/postnummer/',
        data: { zipcode: zipcode },
        type: 'POST'
    }).done(function(result) {
        result = JSON.parse(result);
        if(result.area !== undefined) {
            callback({
                'success': true,
                'area': result.area,
            });
        } else if(result.error == "does_not_exist") {
            callback({
                'success': false,
                'error': 'does_not_exist',
            });
        }
    }).fail(function(result) {
        callback({
            'success': false,
            'error': 'technical_failure',
        });
    });
};
