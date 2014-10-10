# encoding: utf-8
from django.conf.urls.defaults import patterns, url
from django.conf import settings

urlpatterns = patterns('',
    # Newly changed URLs: /artikler/ -> /nyheter/ - redirect temporarily
    url(r'^artikler/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': '/nyheter/', 'permanent': True}),

    # More or less permanent local redirects (keep this list short!)
    url(r'^gullgjest/', 'page.views.perform_redirect', kwargs={'url': '/hyttesamler/', 'permanent': True}),
    url(r'^gratis-overnatting/$', 'page.views.perform_redirect', kwargs={'url': '/ung/gratis-overnatting/', 'permanent': True}),
    url(r'^E1/$', 'page.views.perform_redirect', kwargs={'url': '/e1/', 'permanent': True}),
    url(r'^fjelltreff/$', 'page.views.perform_redirect', kwargs={'url': '/fjelltreffen/', 'permanent': True}),
    url(r'^merkehandboka/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.merkehandboka.no/', 'permanent': True}),
    url(r'^nasjonalt-skiltprosjekt/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turskiltprosjektet.no/', 'permanent': True}),

    # Keep old admin-ui for now (difference is /admin/ vs /sherpa/)
    url(r'^admin/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/admin/' % settings.OLD_SITE}),

    # Old static content
    url(r'^img/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/img/' % settings.OLD_SITE}),
    url(r'^images/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/images/' % settings.OLD_SITE}),
    url(r'^album/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/album/' % settings.OLD_SITE}),
    url(r'^files/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/files/' % settings.OLD_SITE}),
    url(r'^share/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/share/' % settings.OLD_SITE}),
    url(r'^turforslag/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ut.no/tur/'}),

    # Old dynamic content that we want directly redirected
    url(r'^activity.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/activity.php' % settings.OLD_SITE}),
    url(r'^article.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE}),
    url(r'^booking.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/booking.php' % settings.OLD_SITE}),
    url(r'^payment/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/payment/' % settings.OLD_SITE}),
    url(r'^list.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/list.php' % settings.OLD_SITE}),
    url(r'^nor-way.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/nor-way.php' % settings.OLD_SITE}),
    url(r'^hytteadmin/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://%s/hytteadmin/' % settings.OLD_SITE}),
    url(r'^gmap.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/gmap.php' % settings.OLD_SITE}),
    url(r'^balsfjord/$', 'page.views.perform_redirect', kwargs={'url': 'http://troms.turistforeningen.no/index.php?fo_id=10333'}),
    url(r'^static.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/static.php' % settings.OLD_SITE}),

    # Old URLs that are still in use somewhere, even though the old site would link correctly
    url(r'^index.php$', 'page.views.redirect_index'),

    # Old dynamic content - special case for cabins; redirect to UT
    url(r'^cabin.php$', 'page.views.redirect_cabin'),

    # Old content that exists here and has new URLs
    url(r'^conditions.php$', 'page.views.perform_redirect', kwargs={'url': '/foremeldinger/', 'permanent': True, 'include_params': False}),

    # Old XML feeds
    url(r'^xml_activity_ut2.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_activity_ut2.php' % settings.OLD_SITE}),
    url(r'^xml_activity_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_activity_ut.php' % settings.OLD_SITE}),
    url(r'^xml_activity_visitnorway.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_activity_visitnorway.php' % settings.OLD_SITE}),
    url(r'^xml_album_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_album_ut.php' % settings.OLD_SITE}),
    url(r'^xml_atom.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_atom.php' % settings.OLD_SITE}),
    url(r'^xml_cabin_trails_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_cabin_trails_ut.php' % settings.OLD_SITE}),
    url(r'^xml_cabin_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_cabin_ut.php' % settings.OLD_SITE}),
    url(r'^xml_changelog_sted.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_changelog_sted.php' % settings.OLD_SITE}),
    url(r'^xml_changelog_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_changelog_ut.php' % settings.OLD_SITE}),
    url(r'^xml_conditions_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_conditions_ut.php' % settings.OLD_SITE}),
    url(r'^xml_group_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_group_ut.php' % settings.OLD_SITE}),
    url(r'^xml_image_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_image_ut.php' % settings.OLD_SITE}),
    url(r'^xml_location2_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_location2_ut.php' % settings.OLD_SITE}),
    url(r'^xml_location_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_location_ut.php' % settings.OLD_SITE}),
    url(r'^xml_sted_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_sted_ut.php' % settings.OLD_SITE}),
    url(r'^xml_trail_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_trail_ut.php' % settings.OLD_SITE}),
    url(r'^xml_trip_ut.php$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/xml_trip_ut.php' % settings.OLD_SITE}),

    # All sites go to old pages with subdomain
    url(ur'^alesund/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://alesund.turistforeningen.no/', 'permanent': True}),
    url(ur'^alta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://alta.turistforeningen.no/', 'permanent': True}),
    url(ur'^ardal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ardal.turistforeningen.no/', 'permanent': True}),
    url(ur'^askoy/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://askoy.turistforeningen.no/', 'permanent': True}),
    url(ur'^aust-agder/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://aust-agder.turistforeningen.no/', 'permanent': True}),
    url(ur'^austevoll/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://austevoll.turistforeningen.no/', 'permanent': True}),
    url(ur'^baerum/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://baerum.turistforeningen.no/', 'permanent': True}),
    url(ur'^balestrand/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://balestrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^bergen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://bergen.turistforeningen.no/', 'permanent': True}),
    url(ur'^bjornhollia/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://bjornhollia.turistforeningen.no/', 'permanent': True}),
    url(ur'^bomlo/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://bomlo.turistforeningen.no/', 'permanent': True}),
    url(ur'^bronnoysund/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://bronnoysund.turistforeningen.no/', 'permanent': True}),
    url(ur'^brurskanken/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://brurskanken.turistforeningen.no/', 'permanent': True}),
    url(ur'^deutsch/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://deutsch.turistforeningen.no/', 'permanent': True}),
    url(ur'^drammen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://drammen.turistforeningen.no/', 'permanent': True}),
    url(ur'^eidsvoll/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://eidsvoll.turistforeningen.no/', 'permanent': True}),
    url(ur'^elverum/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://elverum.turistforeningen.no/', 'permanent': True}),
    url(ur'^english/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://english.turistforeningen.no/', 'permanent': True}),
    url(ur'^etne/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://etne.turistforeningen.no/', 'permanent': True}),
    url(ur'^fannarakhytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://fannarakhytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^finnskogen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://finnskogen.turistforeningen.no/', 'permanent': True}),
    url(ur'^finsehytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://finsehytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^flekkefjord/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://flekkefjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^flora/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://flora.turistforeningen.no/', 'permanent': True}),
    url(ur'^fondsbu/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://fondsbu.turistforeningen.no/', 'permanent': True}),
    url(ur'^foreningsnett/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://foreningsnett.turistforeningen.no/', 'permanent': True}),
    url(ur'^fosen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://fosen.turistforeningen.no/', 'permanent': True}),
    url(ur'^francais/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://francais.turistforeningen.no/', 'permanent': True}),
    url(ur'^froya/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://froya.turistforeningen.no/', 'permanent': True}),
    url(ur'^gaustatoppen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gaustatoppen.turistforeningen.no/', 'permanent': True}),
    url(ur'^geiterygghytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://geiterygghytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjendebu/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gjendebu.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjendesheim/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gjendesheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjovik/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gjovik.turistforeningen.no/', 'permanent': True}),
    url(ur'^glitterheim/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://glitterheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^grimsdalshytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://grimsdalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^gudbrandsdalen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gudbrandsdalen.turistforeningen.no/', 'permanent': True}),
    url(ur'^gulen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://gulen.turistforeningen.no/', 'permanent': True}),
    url(ur'^hadeland/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://hadeland.turistforeningen.no/', 'permanent': True}),
    url(ur'^hammerfest/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://hammerfest.turistforeningen.no/', 'permanent': True}),
    url(ur'^haugesund/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://haugesund.turistforeningen.no/', 'permanent': True}),
    url(ur'^havrefjell/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://havrefjell.turistforeningen.no/', 'permanent': True}),
    url(ur'^hemsedal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://hemsedal.turistforeningen.no/', 'permanent': True}),
    url(ur'^hol/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://hol.turistforeningen.no/', 'permanent': True}),
    url(ur'^holmdstrand/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://holmdstrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^holmestrand/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://holmestrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^horten/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://horten.turistforeningen.no/', 'permanent': True}),
    url(ur'^indrenordfjord/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://indrenordfjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^indreostfold/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://indreostfold.turistforeningen.no/', 'permanent': True}),
    url(ur'^iungsdalshytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://iungsdalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^jotunheimstien/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://jotunheimstien.turistforeningen.no/', 'permanent': True}),
    url(ur'^kalhovd/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kalhovd.turistforeningen.no/', 'permanent': True}),
    url(ur'^keipen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://keipen.turistforeningen.no/', 'permanent': True}),
    url(ur'^kobberhaughytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kobberhaughytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^komdegut/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://komdegut.turistforeningen.no/', 'permanent': True}),
    url(ur'^kongsberg/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kongsberg.turistforeningen.no/', 'permanent': True}),
    url(ur'^kraekkja/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kraekkja.turistforeningen.no/', 'permanent': True}),
    url(ur'^krokan/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://krokan.turistforeningen.no/', 'permanent': True}),
    url(ur'^kvam/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kvam.turistforeningen.no/', 'permanent': True}),
    url(ur'^kvinnherad/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://kvinnherad.turistforeningen.no/', 'permanent': True}),
    url(ur'^laerdal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://laerdal.turistforeningen.no/', 'permanent': True}),
    url(ur'^larvik/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://larvik.turistforeningen.no/', 'permanent': True}),
    url(ur'^leikanger/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://leikanger.turistforeningen.no/', 'permanent': True}),
    url(ur'^lillehammer/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://lillehammer.turistforeningen.no/', 'permanent': True}),
    url(ur'^liomseter/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://liomseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^litlos/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://litlos.turistforeningen.no/', 'permanent': True}),
    url(ur'^lofoten/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://lofoten.turistforeningen.no/', 'permanent': True}),
    url(ur'^luster/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://luster.turistforeningen.no/', 'permanent': True}),
    url(ur'^lysefjorden/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://lysefjorden.turistforeningen.no/', 'permanent': True}),
    url(ur'^midtrenordfjord/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://midtrenordfjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^mogen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://mogen.turistforeningen.no/', 'permanent': True}),
    url(ur'^narvik/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://narvik.turistforeningen.no/', 'permanent': True}),
    url(ur'^nedreglomma/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nedreglomma.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordhordland/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nordhordland.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordkapp/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nordkapp.turistforeningen.no/', 'permanent': True}),
    url(ur'^nord-osterdal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nord-osterdal.turistforeningen.no/', 'permanent': True}),
    url(ur'^nord-salten/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nord-salten.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordstedalseter/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://nordstedalseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^notodden/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://notodden.turistforeningen.no/', 'permanent': True}),
    url(ur'^ntt/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ntt.turistforeningen.no/', 'permanent': True}),
    url(ur'^odal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://odal.turistforeningen.no/', 'permanent': True}),
    url(ur'^odda-ullensvang/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://odda-ullensvang.turistforeningen.no/', 'permanent': True}),
    url(ur'^os/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://os.turistforeningen.no/', 'permanent': True}),
    url(ur'^bcp/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://preikestolen_basecamp.turistforeningen.no/', 'permanent': True}),
    url(ur'^preikestolenbasecamp/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://preikestolen_basecamp.turistforeningen.no/', 'permanent': True}),
    url(ur'^preikestolen_basecamp/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://preikestolen_basecamp.turistforeningen.no/', 'permanent': True}),
    url(ur'^rana/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://rana.turistforeningen.no/', 'permanent': True}),
    url(ur'^rena/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://rena.turistforeningen.no/', 'permanent': True}),
    url(ur'^ringerike/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ringerike.turistforeningen.no/', 'permanent': True}),
    url(ur'^rondanestien/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://rondanestien.turistforeningen.no/', 'permanent': True}),
    url(ur'^rondvassbu/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://rondvassbu.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandefjord/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sandefjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandhaug/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sandhaug.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandnessjoen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sandnessjoen.turistforeningen.no/', 'permanent': True}),
    url(ur'^sauda/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sauda.turistforeningen.no/', 'permanent': True}),
    url(ur'^senja/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://senja.turistforeningen.no/', 'permanent': True}),
    url(ur'^seterengard/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://seterengard.turistforeningen.no/', 'permanent': True}),
    url(ur'^skogadalsboen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://skogadalsboen.turistforeningen.no/', 'permanent': True}),
    url(ur'^snøheim/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://snoheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^sogndal/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sogndal.turistforeningen.no/', 'permanent': True}),
    url(ur'^sognogfjordane/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sognogfjordane.turistforeningen.no/', 'permanent': True}),
    url(ur'^solor/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://solor.turistforeningen.no/', 'permanent': True}),
    url(ur'^solund/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://solund.turistforeningen.no/', 'permanent': True}),
    url(ur'^sorvaranger/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sorvaranger.turistforeningen.no/', 'permanent': True}),
    url(ur'^sotaseter/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sotaseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^stord-fitjar/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://stord-fitjar.turistforeningen.no/', 'permanent': True}),
    url(ur'^stranddalshytta/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://stranddalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^sulitjelma/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://sulitjelma.turistforeningen.no/', 'permanent': True}),
    url(ur'^svukuriset/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://svukuriset.turistforeningen.no/', 'permanent': True}),
    url(ur'^telemark/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://telemark.turistforeningen.no/', 'permanent': True}),
    url(ur'^troms/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://troms.turistforeningen.no/', 'permanent': True}),
    url(ur'^tvedestrand_og_vegarshei/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://tvedestrand_og_vegarshei.turistforeningen.no/', 'permanent': True}),
    url(ur'^valdres/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://valdres.turistforeningen.no/', 'permanent': True}),
    url(ur'^vansjo/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://vansjo.turistforeningen.no/', 'permanent': True}),
    url(ur'^varangerhalvoya/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://varangerhalvoya.turistforeningen.no/', 'permanent': True}),
    url(ur'^vesteralen/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://vesteralen.turistforeningen.no/', 'permanent': True}),
    url(ur'^vik/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://vik.turistforeningen.no/', 'permanent': True}),
    url(ur'^voss/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://voss.turistforeningen.no/', 'permanent': True}),
    url(ur'^ynt/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ynt.turistforeningen.no/', 'permanent': True}),
    url(ur'^ytresogn/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://ytresogn.turistforeningen.no/', 'permanent': True}),

    # Old site-redirects (misspelled names, shortcuts etc), link directly to the old site domain
    url(r'^aot/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://aust-agder.turistforeningen.no/'}),
    url(r'^aat/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://aust-agder.turistforeningen.no/'}),
    url(r'^austagder/$', 'page.views.perform_redirect', kwargs={'url': 'http://aust-agder.turistforeningen.no/'}),
    url(r'^bodo/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.bot.no/'}),
    url(r'^bronnoy/$', 'page.views.perform_redirect', kwargs={'url': 'http://bronnoysund.turistforeningen.no/'}),
    url(r'^bergen/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.bergen-turlag.no'}),
    url(r'^dntoslo/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntoslo.no/'}),
    url(r'^fredrikstad/$', 'page.views.perform_redirect', kwargs={'url': 'http://nedreglomma.turistforeningen.no/'}),
    url(r'^go/$', 'page.views.perform_redirect', kwargs={'url': 'http://gjovik.turistforeningen.no/'}),
    url(r'^gtt/$', 'page.views.perform_redirect', kwargs={'url': 'http://gjovik.turistforeningen.no/'}),
    url(r'^harstad/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.harstad-turlag.no'}),
    url(r'^httur/$', 'page.views.perform_redirect', kwargs={'url': 'http://haugesund.turistforeningen.no/'}),
    url(r'^preikestolhytta/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.preikestolenfjellstue.no'}),
    url(r'^preikestolenfjellstue/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.preikestolenfjellstue.no'}),
    url(r'^sel/$', 'page.views.perform_redirect', kwargs={'url': 'http://gudbrandsdalen.turistforeningen.no/'}),
    url(r'^skientelemark/$', 'page.views.perform_redirect', kwargs={'url': 'http://skientelemark.turistforeningen.no/'}),
    url(r'^smaalenene/$', 'page.views.perform_redirect', kwargs={'url': 'http://indreostfold.turistforeningen.no/'}),
    url(r'^snoheim/$', 'page.views.perform_redirect', kwargs={'url': 'http://snoheim.turistforeningen.no/'}),
    url(r'^sot/$', 'page.views.perform_redirect', kwargs={'url': 'http://sulitjelma.turistforeningen.no/'}),
    url(r'^sotaseter2/$', 'page.views.perform_redirect', kwargs={'url': 'http://sotaseter.turistforeningen.no/'}),
    url(r'^stavanger/(?P<slug>.*)', 'page.views.perform_redirect', kwargs={'url': 'http://www.stavanger-turistforening.no/'}),
    url(r'^tromsturlag/$', 'page.views.perform_redirect', kwargs={'url': 'http://troms.turistforeningen.no/'}),
    url(r'^telemark/ung/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntung.no/telemark/'}),
    url(r'^troms/barn/$', 'page.views.perform_redirect', kwargs={'url': 'http://troms.turistforeningen.no/group.php', 'params': {'gr_id': '183'}}),
    url(r'^strandalshytta/$', 'page.views.perform_redirect', kwargs={'url': 'http://stranddalshytta.turistforeningen.no/'}),
    url(r'^yst/$', 'page.views.perform_redirect', kwargs={'url': 'http://ytresogn.turistforeningen.no/'}),

    # Old redirects, keep them at the old site
    url(r'^140/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '6007'}}),
    url(r'^aktiviteter/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/activity.php' % settings.OLD_SITE, 'params': {'fo_id': '2513'}}),
    url(r'^aretsgave/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/aretsgave.php' % settings.OLD_SITE}),
    url(r'^butikk/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '435'}}),
    url(r'^daltilfjell/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '11201'}}),
    url(r'^endeligmedlem/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/files/DNT/Endelig%%20medlem' % settings.OLD_SITE}),
    url(r'^engerdalogtrysil/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/group.php' % settings.OLD_SITE, 'params': {'gr_id': '16', 'fo_id': '128'}}),
    url(r'^evaluering/$', 'page.views.perform_redirect', kwargs={'url': 'http://response.questback.com/DenNorskeTuristforening/landsmotet2005/'}),
    url(r'^faktaark/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/files/DNT/Intranett/Faktaark/' % settings.OLD_SITE}),
    url(r'^film/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '11194', 'fo_id': '15'}}),
    url(r'^fjellfest/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '8152', 'fo_id': '15'}}),
    url(r'^fjellfesten/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '8152', 'fo_id': '15'}}),
    url(r'^fjellforing/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntfjellsport.no/index.php', 'params': {'fo_id' '176'}}),
    url(r'^fjellogviddespesial/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.calameo.com/read/0002483005e90ae80224e'}),
    url(r'^fjellvett/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '184'}}),
    url(r'^gaver/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '3160'}}),
    url(r'^grensesommen/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/turplanlegger/trip.php' % settings.OLD_SITE, 'params': {'ac_id': '7438'}}),
    url(r'^hyttedrift/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '4883'}}),
    url(r'^intranett/$', 'page.views.perform_redirect', kwargs={'url': 'http://foreningsnett.turistforeningen.no/'}),
    url(r'^ist/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.istur.no/'}),
    url(r'^kvistekart/$', 'page.views.perform_redirect', kwargs={'url': '/vintermerking/'}),
    url(r'^lokalmat/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '2049'}}),
    url(r'^marked/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/classified.php' % settings.OLD_SITE}),
    url(r'^markedsplassen/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/classified.php' % settings.OLD_SITE}),
    url(r'^membership/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/english/index.php' % settings.OLD_SITE, 'params': {'fo_id': '3606'}}),
    url(r'^nettbutikk/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntbutikken.no/'}),
    url(r'^internbutikk/$', 'page.views.perform_redirect', kwargs={'url': 'http://internbutikk.turistforeningen.no/'}),
    url(r'^paaske/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '7473'}}),
    url(r'^pressearkiv/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/pressearkiv/' % settings.OLD_SITE}),
    url(r'^profil/$', 'page.views.perform_redirect', kwargs={'url': 'http://foreningsnett.turistforeningen.no/file.php', 'params': {'dir': '/Kommunikasjon/Profilprogram', 'fo_id': '6691'}}),
    url(r'^profilprogram/$', 'page.views.perform_redirect', kwargs={'url': 'http://foreningsnett.turistforeningen.no/file.php', 'params': {'dir': '/Kommunikasjon/Profilprogram', 'fo_id': '6691'}}),
    url(r'^ruteinntegning/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/ruteinntegning.pdf' % settings.OLD_SITE}),
    url(r'^skred/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '6285', 'fo_id': '2714'}}),
    url(r'^sor-varanger/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/group.php' % settings.OLD_SITE, 'params': {'gr_id': '48', 'fo_id': '128'}}),
    url(r'^sotajazz/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '8151', 'fo_id': '2419'}}),
    url(r'^telenorbarn/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/form2.php' % settings.OLD_SITE, 'params': {'form': 'telenorbarn'}}),
    url(r'^tester/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '2771'}}),
    url(r'^turbosvar/$', 'page.views.perform_redirect', kwargs={'url': 'http://response.questback.com/dennorsketuristforening/ud57ujnxnk/'}),
    url(r'^varanger/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/group.php' % settings.OLD_SITE, 'params': {'gr_id': '51', 'fo_id': '128'}}),
    url(r'^skredkurs/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/activity.php' % settings.OLD_SITE, 'params': {'ac_cat': 'skredkurs', 'fo_id': '9024'}}),
    url(r'^matogreise/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.matogreiseliv.no'}),
    url(r'^francaise/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/francais/' % settings.OLD_SITE}),
    url(r'^kartbutikken/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntbutikken.no/'}),
    url(r'^kartbutikk/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.dntbutikken.no/'}),
    url(r'^skolecamp/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.skolecamp.no/'}),
    url(r'^buss/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/article.php', 'params': {'ar_id': '10549', 'fo_id': '311'}}),
    url(r'^engerdalogtrysil/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/group.php' % settings.OLD_SITE, 'params': {'gr_id': '16', 'fo_id': '128'}}),
    url(r'^medlemsfordeler/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '3814'}}),
    url(r'^girofeil/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/article.php' % settings.OLD_SITE, 'params': {'ar_id': '25749', 'fo_id': '15'}}),
    url(r'^donald/$', 'page.views.perform_redirect', kwargs={'url': 'http://innmelding.turistforeningen.no'}),
    url(r'^komdegut/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/komdegut/index.php'}),
    url(r'^singeltur/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/activity.php' % settings.OLD_SITE, 'params': {'fo_id': '2513', 'search_string': '', 'ac_cat': 'singeltur'}}),
    url(r'^blogg/$', 'page.views.perform_redirect', kwargs={'url': 'http://blogg.turistforeningen.no/'}),
    url(r'^sykkelturforslag/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/sykkelturforslag/index.php'}),
    url(r'^fyr/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/article.php', 'params': {'ar_id': '27945'}}),
    url(r'^hyttefoto/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/form2.php', 'params': {'form': 'hyttebilder'}}),
    url(r'^era2012/$', 'page.views.perform_redirect', kwargs={'url': 'http://www.turistforeningen.no/english/form2.php', 'params': {'form': 'era12'}}),
    url(r'^gullnokkel/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/index.php' % settings.OLD_SITE, 'params': {'fo_id': '9786'}}),
    url(r'^kitekurs/$', 'page.views.perform_redirect', kwargs={'url': 'http://%s/activity.php' % settings.OLD_SITE, 'params': {'ac_cat': 'kiting', 'fo_id': '9893'}}),
)
