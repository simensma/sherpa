$(document).ready(function() {

    var verification = $("div.enrollment-verification");
    var form = verification.find("form#verification");
    var price_table = verification.find("table.prices");

    /**
     * Calculate who should be the main user.
     *  - Either the cheapest choice,
     *  - or if there is no price difference; the first registered user.
     */
    if(price_table.find("tr.main").length === 0) {
        var high, low;
        var users = price_table.find("tr[data-age]");
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
                if(agePrice > Turistforeningen.price_household) {
                    totalPrice += Turistforeningen.price_household;
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
            price_table.find("tr[data-age]").eq(low.index).addClass('main').find("input[name='main']").click();
            var hint = verification.find("div.errors div.cheaper-mainmember-hint");
            hint.find("span.name").text(low.name);
            hint.find("span.type").text(typeOf(low.age).toLowerCase());
            hint.show();
        } else {
            // No price differences, set the first member as main member
            var done = false;
            price_table.find("tr[data-age]").each(function() {
                if(done) {
                    return;
                }
                if($(this).attr('data-age') > 18) {
                    $(this).addClass('main').find("input[name='main']").click();
                    done = true;
                }
            });
        }
    }

    form.find("a.verify").click(function() {
        var main = price_table.find("tr.main");
        if(main.attr('data-index') !== undefined) {
            form.find("input[name='main-member']").val(main.attr('data-index'));
        }
        form.submit();
    });

    calculatePrices();
    orderListByAge();
    price_table.find("input[name='main']").click(function() {
        price_table.find("tr").removeClass('main');
        $(this).parents("tr").addClass('main');
        calculatePrices();
    });

    function orderListByAge() {
        var rows = [];
        var main = price_table.find("tr.main");
        var jrows = price_table.find("tr[data-index]");
        main.detach();
        jrows.each(function() {
            rows.push($(this));
        }).detach();
        rows.sort(function(a, b) {
            return a.attr('data-age') - b.attr('data-age');
        });
        for(var i=0; i<rows.length; i++) {
            price_table.find("tbody").prepend(rows[i]);
        }
        price_table.find("tbody").prepend(main);
    }

    function calculatePrices() {
        var totalPrice = 0;
        price_table.find("td span.keyprice").each(function() {
            totalPrice += Number($(this).text());
        });
        price_table.find("span.yearbook-price").each(function() {
            totalPrice += Number($(this).text());
        });
        price_table.find("tr[data-index]").each(function() {
            var age = $(this).attr('data-age');
            var price = priceOf(age);
            var type = typeOf(age);
            if(!$(this).hasClass('main') && $(this).siblings(".main").length > 0) {
                if(price > Turistforeningen.price_household) {
                    price = Turistforeningen.price_household;
                    type = Turistforeningen.membership_type_names.household;
                }
            }
            $(this).find("td.type").text(type);
            $(this).find("span.price").text(price);
            totalPrice += price;
        });
        price_table.find("span.totalprice").text(totalPrice);
    }

    function priceOf(age) {
        if(age >= Turistforeningen.age_senior)       return Turistforeningen.price_senior;
        else if(age >= Turistforeningen.age_main)    return Turistforeningen.price_main;
        else if(age >= Turistforeningen.age_youth)   return Turistforeningen.price_youth;
        else if(age >= Turistforeningen.age_school)  return Turistforeningen.price_school;
        else                                         return Turistforeningen.price_child;
    }

    function typeOf(age) {
        if(age >= Turistforeningen.age_senior)       return Turistforeningen.membership_type_names.senior;
        else if(age >= Turistforeningen.age_main)    return Turistforeningen.membership_type_names.main;
        else if(age >= Turistforeningen.age_youth)   return Turistforeningen.membership_type_names.youth;
        else if(age >= Turistforeningen.age_school)  return Turistforeningen.membership_type_names.school;
        else                                         return Turistforeningen.membership_type_names.child;
    }
});

