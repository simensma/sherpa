var price_key = 100;
var price_main = 550;
var price_household = 250;
var price_senior = 425;
var price_student = 295;
var price_school = 175;
var price_child = 110;

$(document).ready(function() {

    /**
     * Calculate who should be the main user.
     *  - Either the cheapest choice,
     *  - or if there is no price difference; the first registered user.
     */
    if($("table.prices tr.main").length == 0) {
        var high, low;
        var users = $("table.prices tr[data-age]");
        users.each(function() {
            if($(this).attr('data-age') <= 18) {
                // 18 and below can't be main members, so ignore this result
                return;
            }
            var main = $(this);
            var totalPrice = 0;
            totalPrice += priceOf($(this).attr('data-age'));
            users.each(function() {
                if($(this).get(0) == main.get(0)) {
                    return;
                }
                var agePrice = priceOf($(this).attr('data-age'));
                if(agePrice > price_household) {
                    totalPrice += price_household;
                } else {
                    totalPrice += agePrice;
                }
            });
            var row = {
                index: $(this).index(),
                price: totalPrice,
                name: $(this).attr('data-name'),
                age: $(this).attr('data-age')
            };
            if(high === undefined || row.price > high.price) {
                high = row;
            }
            if(low === undefined || row.price < low.price) {
                low = row;
            }
        });

        if(high != low) {
            // Recommend the cheapest price
            $("table.prices tr[data-age]").eq(low.index).addClass('main');
            var info = $('<div class="offset3 span6"><div class="alert alert-info"><a class="close">x</a><strong><i class="icon-exclamation-sign"></i> Rabattmulighet</strong><br>Siden ' + low.name + ' er ' + typeOf(low.age).toLowerCase() + ', har vi anbefalt å sette ham/henne som hovedmedlem i husstanden, da det vil være billigst. Du kan endre dette hvis du ønsker.</div></div>');
            info.find("a.close").click(function() { $(this).parent().remove(); });
            $("table.prices").parent().before(info);
        } else {
            // No price differences, set the first member as main member
            var done = false;
            $("table.prices tr[data-age]").each(function() {
                if(done) {
                    return;
                }
                if($(this).attr('data-age') > 18) {
                    $(this).addClass('main');
                    done = true;
                }
            });
        }
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
        if(!$(this).hasClass('main') && $(this).siblings(".main").length > 0) {
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
