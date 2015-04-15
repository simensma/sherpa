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
            # The user claims to be a member if they've given a memberid
            claims_membership = losji['medlemsnummer'] is not None

            # Business rule: Anyone claiming to be a member will get a membership price
            pays_membership_price = claims_membership

            # Check if we can relate this visitor to a user
            user = None
            memberid_unrecognized = None
            if losji['medlemsnummer'] is not None:
                try:
                    user = User.get_or_create_inactive(memberid=losji['medlemsnummer'], include_pending=True)
                    # Note that this is where we could verify that the member has paid their annual fee, but it is
                    # currently ignored
                except (Actor.DoesNotExist, Enrollment.DoesNotExist):
                    # We received an unrecognized memberid, but we'll still allow the purchase, so save the given
                    # memberid for future reference, whatever it is
                    memberid_unrecognized = losji['medlemsnummer']

            cabin_visitor = CabinVisitor(
                cabin_visit=cabin_visit,
                protocol_number=losji['protokollnummer'],
                user=user,
                memberid_unrecognized=memberid_unrecognized,
            )
            cabin_visitor.save()

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
