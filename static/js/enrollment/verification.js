var price_key = 100;
var price_main = 550;
var price_household = 250;
var price_senior = 425;
var price_student = 295;
var price_school = 175;
var price_child = 110;

$(document).ready(function() {

    calculatePrices();
    $("select.main").change(function(e) {
        $("table.prices tr").removeClass('main');
        $("table.prices tr[data-index='" + $(this).find("option:selected").val() + "']").addClass('main');
        calculatePrices();
    });
});

function calculatePrices() {
    var totalPrice = 0;
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
    } else if(age <= 26 && age > 19) {
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
    } else if(age <= 26 && age > 19) {
        return 'Student/ungdomsmedlem';
    } else if(age <= 18 && age > 13) {
        return 'Skoleungdomsmedlem';
    } else if(age <= 13) {
        return 'Barnemedlem';
    }
}
