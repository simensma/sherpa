# encoding: utf-8
from focus.models import Actor, Enrollment
from foreninger.models import Forening, Supply
from turbasen.models import Sted
from user.models import User, CabinSettlement, CabinVisit, CabinVisitor

def cabin_visit(product_data):
    # Okay, initiate a settlement
    cabin_settlement = CabinSettlement(
        order_number=CabinSettlement.generate_order_number(),
    )
    cabin_settlement.save()

    # @TODO: OAuth

    amount = 0
    for cabin in product_data['hytter']:
        sted = Sted.get(cabin["id"])
        # @TODO: Handle cabins with multiple owners (defaulting to first occurrence for now)
        forening = Forening.objects.get(turbase_object_id=sted.grupper[0])

        cabin_visit = CabinVisit(
            cabin_settlement=cabin_settlement,
            cabin_object_id=sted.object_id,
        )
        cabin_visit.save()

        for losji in cabin['losji']:
            cabin_visitor = CabinVisitor(
                cabin_visit=cabin_visit,
                protocol_number=losji['protokollnummer'],
            )
            cabin_visitor.save()

            if losji['medlemsnummer'] is not None:
                try:
                    user = User.get_or_create_inactive(memberid=losji['medlemsnummer'], include_pending=True)
                    if not user.has_paid():
                        # @TODO: confirm in the client that one or more users aren't valid
                        raise NotImplementedError

                    cabin_visitor.user = user
                    cabin_visitor.save()
                except (Actor.DoesNotExist, Enrollment.DoesNotExist):
                    # @TODO: handle invalid memberid
                    raise NotImplementedError

        for proviant in cabin['proviant']:
            supply = Supply.objects.get(
                id=proviant['id'],
                supply_category__forening=forening.id,
            )

            # Business rule: The supply price is determined by whether or not the paying user is considered a member
            if product_data['medlemspris']:
                amount += supply.price_member * proviant['antall']
            else:
                amount += supply.price_nonmember * proviant['antall']

    return (amount, cabin_settlement.order_number)
