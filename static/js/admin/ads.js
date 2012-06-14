function uploadComplete(result) {
    if(result == 'success') {
        location.reload(true);
    } else if(result == 'parse_error') {
        // TODO
    } else if(result == 'no_files') {
        // TODO
    }
}
