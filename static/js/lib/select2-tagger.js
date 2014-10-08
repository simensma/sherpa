/**
 * Utility function to apply a select2 tagger to an input element.
 * Options:
 * $input: The input element to enable select2 on
 *
 * The input element is expected to contain the following attributes:
 * data-dnt-tags-url: The URL to the ajax backend endpoint
 * data-dnt-existing-tags: A JSON array of tags to include in the input by default
 */
function Select2Tagger(opts) {
    opts.$input.select2({
        formatSearching: 'Søker etter liknende nøkkelord...',
        formatInputTooShort: function (input, min) {
            // Ignore search characters, just tell users that they can search
            return "Skriv inn nøkkelord...";
        },
        multiple: true,
        createSearchChoice: function(term, data) {
            return {id:term, text:term};
        },
        tokenSeparators: [',', ' '],
        minimumInputLength: 3,
        initSelection : function(element, callback) {
            var data = [];
            $(element.val().split(',')).each(function() {
                data.push({id: this, text: this});
            });
            callback(data);
        },
        ajax: {
            url: opts.$input.attr('data-dnt-tags-url'),
            dataType: 'json',
            data: function(term, page) {
                return {q: term};
            },
            results: function(data, page) {
                return {results: data};
            }
        },
    }).select2('val', JSON.parse(opts.$input.attr('data-dnt-existing-tags')));
}
