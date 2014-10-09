/**
 * Utility function to apply select2 autocomplete to an input element.
 * Options:
 * $input: The input element to enable select2 on
 *
 * The input element is expected to contain the following attributes:
 * data-dnt-lookup-url: The URL to the ajax backend endpoint
 */
function Select2Input(opts) {
    opts.$input.select2({
        formatSearching: 'Søker...',
        formatInputTooShort: function(input, min) {
            // Ignore search characters, just tell users that they can search
            return "Skriv inn nøkkelord...";
        },
        createSearchChoice: function(term, data) {
            return {id:term, text:term};
        },
        minimumInputLength: 3,
        initSelection : function(element, callback) {
            var data = [];
            $(element.val().split(',')).each(function() {
                data.push({id: this, text: this});
            });
            callback(data);
        },
        ajax: {
            url: opts.$input.attr('data-dnt-lookup-url'),
            dataType: 'json',
            data: function(term, page) {
                return {q: term};
            },
            results: function(data, page) {
                return {results: data};
            }
        },
    });
}
