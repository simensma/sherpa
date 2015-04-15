# encoding: utf-8
from focus.models import Actor, Enrollment
from foreninger.models import Forening, Supply
from turbasen.models import Sted
from user.models import User, CabinVisit, CabinVisitor

def cabin_visit(product_data):
    sted = Sted.get(product_data['hytte'])
    # TODO: Handle cabins with multiple owners (defaulting to first occurrence for now)
    forening = Forening.objects.get(turbase_object_id=sted.grupper[0])

    cabin_visit = CabinVisit(
        order_number=CabinVisit.generate_order_number(),
    )
    cabin_visit.save()

    amount = 0
    for gjest in product_data['gjester']:
        cabin_visitor = CabinVisitor(
            cabin_visit=cabin_visit,
            protocol_number=gjest['protokollnummer'],
        )
        cabin_visitor.save()

        if gjest['medlemsnummer'] is None:
            is_member = False
        else:
            try:
                user = User.get_or_create_inactive(memberid=gjest['medlemsnummer'], include_pending=True)
                if not user.has_paid():
                    # TODO: confirm in the client that one or more users aren't valid
                    raise NotImplementedError
                is_member = True

                cabin_visitor.user = user
                cabin_visitor.save()
            except (Actor.DoesNotExist, Enrollment.DoesNotExist):
                # TODO: handle invalid memberid
                raise NotImplementedError

        for losji in gjest['losji']:
            lodging = forening.lodging_prices.get(id=losji['id'])
            if is_member:
                amount += lodging.price_member * losji['antall']
            else:
                amount += lodging.price_nonmember * losji['antall']

        for proviant in gjest["proviant"]:
            supply = Supply.objects.get(
                id=proviant['id'],
                supply_category__forening=forening.id,
            )
            if is_member:
                amount += supply.price_member * proviant['antall']
            else:
                amount += supply.price_nonmember * proviant['antall']

    return (amount, cabin_visit.order_number)
