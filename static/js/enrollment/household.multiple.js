$(document).ready(function() {

    $("div.existing").hide();
    setDefaultMain();
    $("table.main-member button.choose-member").click(function(event) {
        event.preventDefault();
        setMain($(this).parents("tr[data-age]"));
    });

    $("input.existing").click(function() {
        if($(this).prop('checked')) {
            $("table.main-member tr.main").removeClass('main');
            $("table.main-member button.choose-member").css('visibility', 'hidden');
            $("table.main-member tr th").eq(2).hide();
            $("div.existing").show();
            traverseMembershipTypes();
        } else {
            $("div.existing").hide();
            setDefaultMain();
            $("table.main-member tr th").eq(2).show();
        }
    });

    $("form#household").submit(function() {
        if($(this).children("input.existing").prop('checked')) {
            // Send the main member index
            $(this).append('<input type="hidden" name="main-index" value="' +
                $("table.main-member tr.main").attr('data-index') + '">');
        } else {
            $(this).children("input[name='existing']").remove();
        }
    });

    function setMain(tr) {
        $("table.main-member button.choose-member").css('visibility', 'visible');
        $("table.main-member tr.main").removeClass('main');
        tr.find("button.choose-member").css('visibility', 'hidden');
        tr.addClass('main');
        traverseMembershipTypes();
    }

    function setDefaultMain() {
        var mainAge = 0;
        $("table.main-member tr[data-age]").each(function() {
            var age = $(this).attr('data-age');
            if(age >= 13) {
                if(age > mainAge) {
                    setMain($(this));
                    mainAge = age;
                }
            } else {
                $(this).find("button.choose-member").remove();
            }
        });
    }

    function traverseMembershipTypes() {
        $("table.main-member tr[data-age]").each(function() {
            var age = $(this).attr('data-age');
            var membershipType;
            if($(this).hasClass('main')) {
                if(age > 66) {
                    membershipType = 'Hovedmedlem (honnør)';
                } else if(age <= 66 && age > 26) {
                    membershipType = 'Hovedmedlem';
                } else if(age <= 26 && age > 19) {
                    membershipType = 'Hovedmedlem (student/ungdom)';
                } else if(age <= 18 && age > 13) {
                    membershipType = 'Hovedmedlem (skole)';
                }
            } else {
                if(age > 66) {
                    membershipType = 'Husstandsmedlem (honnør)';
                } else if(age <= 66 && age > 26) {
                    membershipType = 'Husstandsmedlem';
                } else if(age <= 26 && age > 19) {
                    membershipType = 'Husstandsmedlem (student/ungdom)';
                } else if(age <= 18 && age > 13) {
                    membershipType = 'Husstandsmedlem (skole)';
                } else if(age <= 13) {
                    membershipType = 'Husstandsmedlem (barn)';
                }
            }
            $(this).children("td.membershipType").text(membershipType);
        });
    }

});
