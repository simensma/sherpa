/**
 * The common use case for typeahed.
 *
 * Options:
 * url: The remote ajax URL
 * $input: The jquery input element to enable typeahead on
 */
function SimpleTypeahead(opts) {
    var bloodhound_engine = new Bloodhound({
        datumTokenizer: function(d) {
            return Bloodhound.tokenizers.whitespace(d.val);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: opts.url + "?q=%QUERY",
    });
    bloodhound_engine.initialize();

    opts.$input.typeahead({
        minLength: 3,
        highlight: true,
    }, {
        source: bloodhound_engine.ttAdapter()
    });
}
