$(document).ready(function() {

    // Hide inputs by default
    $("form#household div.household").css('visibility', 'hidden');
    $("form#household div.existing").css('visibility', 'hidden');
    $("form#household th").eq(2).css('visibility', 'hidden');

    // User changes state
    $("form#household input[name='household']").click(changeState);
    $("form#household select").change(changeState);

    function changeState() {
        // Start with a clean state
        $("form#household th").eq(2).css('visibility', 'hidden');
        var inputs = $("form#household input[name='household']");
        inputs.removeAttr('disabled').parent().css('text-decoration', 'none');
        $("form#household option").removeAttr('disabled');

        // Now figure out the current state
        inputs.each(function() {
            var nextCol = $(this).parent().next();
            if($(this).prop('checked')) {
                // This is a household member
                $("form#household th").eq(2).css('visibility', 'visible');
                nextCol.children("div.household").css('visibility', 'visible');

                // Disabled picking this member as main member
                $("form#household select option[value='" + $(this).attr('data-index') + "']").attr('disabled', true);

                // Traverse the main member selection
                nextCol.find("option:selected").each(function() {
                    if($(this).val() == 'existing') {
                        $(this).parent().next().css('visibility', 'visible');
                    } else {
                        // Disabled picking the chosen connected-member as household member
                        $(this).parent().next().css('visibility', 'hidden');
                        $("form#household input[data-index='" + $(this).val() + "']").attr('disabled', true).parent().css('text-decoration', 'line-through');
                    }
                });
            } else {
                // Not a household member anymore, reset the state
                nextCol.find("div.household, div.existing").css('visibility', 'hidden');
                nextCol.find("select option:first-child").prop('selected', true);
            }
        });
    }
});
