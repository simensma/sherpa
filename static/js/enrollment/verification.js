var price_key = 100;
var price_main = 550;
var price_household = 250;
var price_senior = 425;
var price_student = 295;
var price_school = 175;
var price_child = 110;

$(document).ready(function() {

    // Figure out the initial main user - the one with lowest age over 18
    if($("table.prices tr.main").length == 0) {
        var current;
        $("table.prices tr[data-age]").each(function() {
            var age = $(this).attr('data-age');
            if(current === undefined || (age < current.attr('data-age') && age > 18)) {
                current = $(this);
            }
        });
        current.addClass('main');
    }

    calculatePrices();
    orderListByAge();
    $("table.prices tr.main button").hide();
    $("table.prices tr span.main").hide();
    $("table.prices tr.main span.main").show();
    $("table.prices button.main").click(function(e) {
        $("table.prices tr").removeClass('main');
        $(this).parents("tr").addClass('main');
        $("table.prices button").show();
        $("table.prices tr.main button").hide();
        $("table.prices tr span.main").hide();
        $("table.prices tr.main span.main").show();
        calculatePrices();
    });

});

function orderListByAge() {
    var rows = [];
    var main = $("table.prices tr.main");
    var jrows = $("table.prices tr[data-index]");
    main.detach();
    jrows.each(function() {
        rows = rows.concat([$(this)]);
    }).detach();
    rows.sort(function(a, b) {
        return a.attr('data-age') - b.attr('data-age');
    });
    for(var i=0; i<rows.length; i++) {
        $("table.prices tbody").prepend(rows[i]);
    }
    $("table.prices tbody").prepend(main);
}

function calculatePrices() {
    var totalPrice = 0;
    $("table.prices td[data-key] span.keyprice").each(function() {
        totalPrice += Number($(this).text());
    });
    $("table.prices tr[data-index]").each(function() {
        var age = $(this).attr('data-age');
        var price = priceOf(age);
        var type = typeOf(age);
        if(!$(this).hasClass('main')) {
            if(price > price_household) {
                price = price_household;
                type = "Husstandsmedlem";
            }
        }
        $(this).find("td.type").text(type);
        $(this).find("span.price").text(price);
        totalPrice += price;
    });
    $("table.prices span.totalprice").text(totalPrice);
}

function priceOf(age) {
    if(age > 66) {
        return price_senior;
    } else if(age <= 66 && age > 26) {
        return price_main;
    } else if(age <= 26 && age > 18) {
        return price_student;
    } else if(age <= 18 && age > 13) {
        return price_school;
    } else if(age <= 13) {
        return price_child;
    }
}

function typeOf(age) {
    if(age > 66) {
        return 'Honnørmedlem';
    } else if(age <= 66 && age > 26) {
        return 'Hovedmedlem';
    } else if(age <= 26 && age > 18) {
        return 'Student/ungdomsmedlem';
    } else if(age <= 18 && age > 13) {
        return 'Skoleungdomsmedlem';
    } else if(age <= 13) {
        return 'Barnemedlem';
    }
}
