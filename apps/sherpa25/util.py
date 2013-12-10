from core.models import County
from fjelltreffen.models import Annonse
from sherpa2.util import SHERPA2_COUNTIES_SET2 as SHERPA2_COUNTIES
from sherpa25.models import Link, Member, Classified, ClassifiedImage

def import_fjelltreffen_annonser(user):
    old_member = Member.objects.get(memberid=user.memberid)

    for link in Link.objects.filter(fromobject='Member', fromid=old_member.id, toobject='Classified'):
        try:
            # Check for any saved images, and see if we can determine a usable path
            imageid = Link.objects.get(fromobject='Classified', fromid=link.toid, toobject='ClassifiedImage').toid
            path = ClassifiedImage.objects.get(id=imageid).path
            if path.startswith('/var/www/hosts/turistforeningen.no/web/img/fjelltreff/'):
                # This one is served on the old site and still usable
                old_annonse_imageurl = path.split('/var/www/hosts/turistforeningen.no/web/')[1]
            elif path.startswith('/www/sherpa2/www/dnt/img/fjelltreff/'):
                # This one is served on the old site and still usable
                old_annonse_imageurl = path.split('/www/sherpa2/www/dnt/')[1]
            else:
                # Unknown path, or known unusable path - ignore this image.
                old_annonse_imageurl = ''
        except (Link.DoesNotExist, ClassifiedImage.DoesNotExist):
            old_annonse_imageurl = ''
        try:
            old_annonse = Classified.objects.get(id=link.toid)
        except Classified.DoesNotExist:
            continue

        annonse = Annonse()
        annonse.user = user
        annonse.title = old_annonse.title

        # Email is required, so make sure we find one for the old user
        if old_member.email is None or old_member.email == '':
            # Nope, it's not here. Try to get it from Focus
            focus_email = user.get_email()
            if focus_email == '':
                # Not in Focus either! We'll have to ignore this annonse.
                continue
            else:
                # Ok, use the focus email
                annonse.email = focus_email
        else:
            annonse.email = old_member.email

        try:
            annonse.county = County.objects.get(code=SHERPA2_COUNTIES[old_annonse.county])
        except KeyError:
            if old_annonse.county == 0:
                # The entire country is no longer applicable - set it to the Actor's county
                annonse.county = user.get_address().county
            elif old_annonse.county == 2:
                # Both Oslo and Akershus - set it to the Actor's county, which hopefully is one of those
                annonse.county = user.get_address().county
            elif old_annonse.county == 99:
                # International annonse - defined with 'NULL'
                annonse.county = None

        annonse.image = old_annonse_imageurl
        annonse.text = old_annonse.content
        annonse.is_image_old = True
        annonse.hidden = True
        annonse.hideage = True

        #hax to prevent autoadd now
        annonse.save()
        annonse.date_added = old_annonse.authorized
        annonse.date_renewed = old_annonse.authorized
        annonse.save()

    # After adding all of them, make sure the newest one (and only the newest one) is visible
    try:
        newest = Annonse.objects.filter(user=user).order_by('-date_added')[0]
        newest.hidden = False
        newest.save()
    except IndexError:
        pass
