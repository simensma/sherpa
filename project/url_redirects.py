# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Keep old admin-ui for now (difference is /admin/ vs /sherpa/)
    url(r'^admin/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/admin/' % settings.OLD_SITE}),

    # Keep old user page
    # Note: This URL uses hardcoded links in enrollment result pages and email receipts.
    url(r'^minside/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/minside/' % settings.OLD_SITE}),
    url(r'^fjelltreffen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/fjelltreffen/' % settings.OLD_SITE}),

    # Old static content
    url(r'^img/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/img/' % settings.OLD_SITE}),
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/images/' % settings.OLD_SITE}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/album/' % settings.OLD_SITE}),
    url(r'^files/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/files/' % settings.OLD_SITE}),

    # All sites go to old pages with subdomain
    url(ur'^alesund/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://alesund.turistforeningen.no/', 'permanent': True}),
    url(ur'^alta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://alta.turistforeningen.no/', 'permanent': True}),
    url(ur'^ardal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://ardal.turistforeningen.no/', 'permanent': True}),
    url(ur'^askoy/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://askoy.turistforeningen.no/', 'permanent': True}),
    url(ur'^aust-agder/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://aust-agder.turistforeningen.no/', 'permanent': True}),
    url(ur'^austevoll/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://austevoll.turistforeningen.no/', 'permanent': True}),
    url(ur'^baerum/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://baerum.turistforeningen.no/', 'permanent': True}),
    url(ur'^balestrand/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://balestrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^bergen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://bergen.turistforeningen.no/', 'permanent': True}),
    url(ur'^bjornhollia/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://bjornhollia.turistforeningen.no/', 'permanent': True}),
    url(ur'^bomlo/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://bomlo.turistforeningen.no/', 'permanent': True}),
    url(ur'^bronnoysund/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://bronnoysund.turistforeningen.no/', 'permanent': True}),
    url(ur'^brurskanken/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://brurskanken.turistforeningen.no/', 'permanent': True}),
    url(ur'^deutsch/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://deutsch.turistforeningen.no/', 'permanent': True}),
    url(ur'^drammen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://drammen.turistforeningen.no/', 'permanent': True}),
    url(ur'^eidsvoll/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://eidsvoll.turistforeningen.no/', 'permanent': True}),
    url(ur'^elverum/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://elverum.turistforeningen.no/', 'permanent': True}),
    url(ur'^english/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://english.turistforeningen.no/', 'permanent': True}),
    url(ur'^etne/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://etne.turistforeningen.no/', 'permanent': True}),
    url(ur'^fannarakhytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://fannarakhytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^finnskogen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://finnskogen.turistforeningen.no/', 'permanent': True}),
    url(ur'^finsehytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://finsehytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^flekkefjord/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://flekkefjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^flora/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://flora.turistforeningen.no/', 'permanent': True}),
    url(ur'^fondsbu/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://fondsbu.turistforeningen.no/', 'permanent': True}),
    url(ur'^foreningsnett/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://foreningsnett.turistforeningen.no/', 'permanent': True}),
    url(ur'^fosen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://fosen.turistforeningen.no/', 'permanent': True}),
    url(ur'^francais/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://francais.turistforeningen.no/', 'permanent': True}),
    url(ur'^gaustatoppen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gaustatoppen.turistforeningen.no/', 'permanent': True}),
    url(ur'^geiterygghytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://geiterygghytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjendebu/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gjendebu.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjendesheim/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gjendesheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^gjovik/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gjovik.turistforeningen.no/', 'permanent': True}),
    url(ur'^glitterheim/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://glitterheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^grimsdalshytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://grimsdalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^gudbrandsdalen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gudbrandsdalen.turistforeningen.no/', 'permanent': True}),
    url(ur'^gulen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://gulen.turistforeningen.no/', 'permanent': True}),
    url(ur'^hadeland/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://hadeland.turistforeningen.no/', 'permanent': True}),
    url(ur'^hammerfest/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://hammerfest.turistforeningen.no/', 'permanent': True}),
    url(ur'^haugesund/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://haugesund.turistforeningen.no/', 'permanent': True}),
    url(ur'^havrefjell/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://havrefjell.turistforeningen.no/', 'permanent': True}),
    url(ur'^hemsedal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://hemsedal.turistforeningen.no/', 'permanent': True}),
    url(ur'^holmdstrand/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://holmdstrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^holmestrand/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://holmestrand.turistforeningen.no/', 'permanent': True}),
    url(ur'^horten/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://horten.turistforeningen.no/', 'permanent': True}),
    url(ur'^indrenordfjord/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://indrenordfjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^indreostfold/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://indreostfold.turistforeningen.no/', 'permanent': True}),
    url(ur'^iungsdalshytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://iungsdalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^jotunheimstien/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://jotunheimstien.turistforeningen.no/', 'permanent': True}),
    url(ur'^kalhovd/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kalhovd.turistforeningen.no/', 'permanent': True}),
    url(ur'^keipen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://keipen.turistforeningen.no/', 'permanent': True}),
    url(ur'^kobberhaughytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kobberhaughytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^komdegut/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://komdegut.turistforeningen.no/', 'permanent': True}),
    url(ur'^kongsberg/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kongsberg.turistforeningen.no/', 'permanent': True}),
    url(ur'^kraekkja/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kraekkja.turistforeningen.no/', 'permanent': True}),
    url(ur'^krokan/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://krokan.turistforeningen.no/', 'permanent': True}),
    url(ur'^kvam/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kvam.turistforeningen.no/', 'permanent': True}),
    url(ur'^kvinnherad/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://kvinnherad.turistforeningen.no/', 'permanent': True}),
    url(ur'^laerdal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://laerdal.turistforeningen.no/', 'permanent': True}),
    url(ur'^larvik/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://larvik.turistforeningen.no/', 'permanent': True}),
    url(ur'^leikanger/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://leikanger.turistforeningen.no/', 'permanent': True}),
    url(ur'^lillehammer/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://lillehammer.turistforeningen.no/', 'permanent': True}),
    url(ur'^liomseter/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://liomseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^litlos/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://litlos.turistforeningen.no/', 'permanent': True}),
    url(ur'^lofoten/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://lofoten.turistforeningen.no/', 'permanent': True}),
    url(ur'^luster/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://luster.turistforeningen.no/', 'permanent': True}),
    url(ur'^lysefjorden/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://lysefjorden.turistforeningen.no/', 'permanent': True}),
    url(ur'^midtrenordfjord/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://midtrenordfjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^mogen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://mogen.turistforeningen.no/', 'permanent': True}),
    url(ur'^narvik/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://narvik.turistforeningen.no/', 'permanent': True}),
    url(ur'^nedreglomma/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nedreglomma.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordhordland/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nordhordland.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordkapp/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nordkapp.turistforeningen.no/', 'permanent': True}),
    url(ur'^nord-osterdal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nord-osterdal.turistforeningen.no/', 'permanent': True}),
    url(ur'^nord-salten/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nord-salten.turistforeningen.no/', 'permanent': True}),
    url(ur'^nordstedalseter/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://nordstedalseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^notodden/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://notodden.turistforeningen.no/', 'permanent': True}),
    url(ur'^ntt/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://ntt.turistforeningen.no/', 'permanent': True}),
    url(ur'^odal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://odal.turistforeningen.no/', 'permanent': True}),
    url(ur'^odda-ullensvang/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://odda-ullensvang.turistforeningen.no/', 'permanent': True}),
    url(ur'^os/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://os.turistforeningen.no/', 'permanent': True}),
    url(ur'^preikestolen_basecamp/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://preikestolen_basecamp.turistforeningen.no/', 'permanent': True}),
    url(ur'^rana/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://rana.turistforeningen.no/', 'permanent': True}),
    url(ur'^rena/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://rena.turistforeningen.no/', 'permanent': True}),
    url(ur'^ringerike/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://ringerike.turistforeningen.no/', 'permanent': True}),
    url(ur'^rondanestien/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://rondanestien.turistforeningen.no/', 'permanent': True}),
    url(ur'^rondvassbu/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://rondvassbu.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandefjord/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sandefjord.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandhaug/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sandhaug.turistforeningen.no/', 'permanent': True}),
    url(ur'^sandnessjoen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sandnessjoen.turistforeningen.no/', 'permanent': True}),
    url(ur'^sauda/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sauda.turistforeningen.no/', 'permanent': True}),
    url(ur'^senja/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://senja.turistforeningen.no/', 'permanent': True}),
    url(ur'^seterengard/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://seterengard.turistforeningen.no/', 'permanent': True}),
    url(ur'^skogadalsboen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://skogadalsboen.turistforeningen.no/', 'permanent': True}),
    url(ur'^snøheim/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://snøheim.turistforeningen.no/', 'permanent': True}),
    url(ur'^sogndal/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sogndal.turistforeningen.no/', 'permanent': True}),
    url(ur'^sognogfjordane/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sognogfjordane.turistforeningen.no/', 'permanent': True}),
    url(ur'^solor/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://solor.turistforeningen.no/', 'permanent': True}),
    url(ur'^solund/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://solund.turistforeningen.no/', 'permanent': True}),
    url(ur'^sorvaranger/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sorvaranger.turistforeningen.no/', 'permanent': True}),
    url(ur'^sotaseter/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sotaseter.turistforeningen.no/', 'permanent': True}),
    url(ur'^stord-fitjar/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://stord-fitjar.turistforeningen.no/', 'permanent': True}),
    url(ur'^stranddalshytta/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://stranddalshytta.turistforeningen.no/', 'permanent': True}),
    url(ur'^sulitjelma/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://sulitjelma.turistforeningen.no/', 'permanent': True}),
    url(ur'^svukuriset/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://svukuriset.turistforeningen.no/', 'permanent': True}),
    url(ur'^telemark/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://telemark.turistforeningen.no/', 'permanent': True}),
    url(ur'^troms/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://troms.turistforeningen.no/', 'permanent': True}),
    url(ur'^tvedestrand_og_vegarshei/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://tvedestrand_og_vegarshei.turistforeningen.no/', 'permanent': True}),
    url(ur'^valdres/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://valdres.turistforeningen.no/', 'permanent': True}),
    url(ur'^vansjo/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://vansjo.turistforeningen.no/', 'permanent': True}),
    url(ur'^varangerhalvoya/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://varangerhalvoya.turistforeningen.no/', 'permanent': True}),
    url(ur'^vesteralen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://vesteralen.turistforeningen.no/', 'permanent': True}),
    url(ur'^vik/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://vik.turistforeningen.no/', 'permanent': True}),
    url(ur'^voss/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://voss.turistforeningen.no/', 'permanent': True}),
    url(ur'^ynt/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://ynt.turistforeningen.no/', 'permanent': True}),
    url(ur'^ytresogn/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://ytresogn.turistforeningen.no/', 'permanent': True}),

    # Old redirects, keep them at the old site
    url(r'^sykkel/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=10173' % settings.OLD_SITE}),
    url(r'^140/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=6007' % settings.OLD_SITE}),
    url(r'^aktiviteter/$', 'page.views.redirect', kwargs={'url': 'http://%s/activity.php?fo_id=2513' % settings.OLD_SITE}),
    url(r'^allemannsretten/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=7371&fo_id=5' % settings.OLD_SITE}),
    url(r'^aretsgave/$', 'page.views.redirect', kwargs={'url': 'http://%s/aretsgave.php' % settings.OLD_SITE}),
    url(r'^austagder/$', 'page.views.redirect', kwargs={'url': 'http://%s/aust-agder' % settings.OLD_SITE}),
    url(r'^bodo/$', 'page.views.redirect', kwargs={'url': 'http://www.bot.no/'}),
    url(r'^bronnoy/$', 'page.views.redirect', kwargs={'url': 'http://%s/bronnoysund/' % settings.OLD_SITE}),
    url(r'^bergen/$', 'page.views.redirect', kwargs={'url': 'http://www.bergen-turlag.no'}),
    url(r'^butikk/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=435' % settings.OLD_SITE}),
    url(r'^daltilfjell/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=11201' % settings.OLD_SITE}),
    url(r'^dntoslo/$', 'page.views.redirect', kwargs={'url': 'http://www2.dntoslo.no/'}),
    url(r'^endeligmedlem/$', 'page.views.redirect', kwargs={'url': 'http://%s/files/DNT/Endelig%%20medlem' % settings.OLD_SITE}),
    url(r'^engerdalogtrysil/$', 'page.views.redirect', kwargs={'url': 'http://%s/group.php?gr_id=16&fo_id=128' % settings.OLD_SITE}),
    url(r'^evaluering/$', 'page.views.redirect', kwargs={'url': 'http://response.questback.com/DenNorskeTuristforening/landsmotet2005/'}),
    url(r'^faktaark/$', 'page.views.redirect', kwargs={'url': 'http://%s/files/DNT/Intranett/Faktaark/' % settings.OLD_SITE}),
    url(r'^film/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=11194&fo_id=15' % settings.OLD_SITE}),
    url(r'^fjellfest/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=8152&fo_id=15' % settings.OLD_SITE}),
    url(r'^fjellfesten/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=8152&fo_id=15' % settings.OLD_SITE}),
    url(r'^fjellforing/$', 'page.views.redirect', kwargs={'url': 'http://www.dntfjellsport.no/index.php?fo_id=176'}),
    url(r'^fjellogviddespesial/$', 'page.views.redirect', kwargs={'url': 'http://www.calameo.com/read/0002483005e90ae80224e'}),
    url(r'^fjelltreff/$', 'page.views.redirect', kwargs={'url': 'http://%s/fjelltreffen' % settings.OLD_SITE}),
    url(r'^fjellvett/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=184' % settings.OLD_SITE}),
    url(r'^foremeldinger/$', 'page.views.redirect', kwargs={'url': 'http://%s/conditions.php?fo_id=3872' % settings.OLD_SITE}),
    url(r'^gavemedlemskap/$', 'page.views.redirect', kwargs={'url': 'http://%s/form2.php?form=gavemedlemskap' % settings.OLD_SITE}),
    url(r'^gaver/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=3160' % settings.OLD_SITE}),
    url(r'^grensesommen/$', 'page.views.redirect', kwargs={'url': 'http://%s/turplanlegger/trip.php?ac_id=7438' % settings.OLD_SITE}),
    url(r'^hyttedrift/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=4883' % settings.OLD_SITE}),
    url(r'^instruktor/$', 'page.views.redirect', kwargs={'url': 'http://www.dntfjellsport.no/activity.php?ac_cat=instruktorkurs&fo_id=229'}),
    url(r'^intranett/$', 'page.views.redirect', kwargs={'url': 'http://%s/foreningsnett' % settings.OLD_SITE}),
    url(r'^ist/$', 'page.views.redirect', kwargs={'url': 'http://www.istur.no/'}),
    url(r'^kvistekart/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=6617&fo_id=4596' % settings.OLD_SITE}),
    url(r'^lokalmat/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=2049' % settings.OLD_SITE}),
    url(r'^marked/$', 'page.views.redirect', kwargs={'url': 'http://%s/classified.php' % settings.OLD_SITE}),
    url(r'^markedsplassen/$', 'page.views.redirect', kwargs={'url': 'http://%s/classified.php' % settings.OLD_SITE}),
    url(r'^membership/$', 'page.views.redirect', kwargs={'url': 'http://%s/english/index.php?fo_id=3606' % settings.OLD_SITE}),
    url(r'^nettbutikk/$', 'page.views.redirect', kwargs={'url': 'http://nettbutikken.turistforeningen.no/eshop'}),
    url(r'^paaske/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=7473' % settings.OLD_SITE}),
    url(r'^pressearkiv/$', 'page.views.redirect', kwargs={'url': 'http://www2.turistforeningen.no/pressearkiv/'}),
    url(r'^profil/$', 'page.views.redirect', kwargs={'url': 'http://%s/foreningsnett/file.php?dir=/Kommunikasjon/Profilprogram&fo_id=6691' % settings.OLD_SITE}),
    url(r'^profilprogram/$', 'page.views.redirect', kwargs={'url': 'http://%s/foreningsnett/file.php?dir=/Kommunikasjon/Profilprogram&fo_id=6691' % settings.OLD_SITE}),
    url(r'^ruteinntegning/$', 'page.views.redirect', kwargs={'url': 'http://%s/ruteinntegning.pdf' % settings.OLD_SITE}),
    url(r'^sel/$', 'page.views.redirect', kwargs={'url': 'http://%s/gudbrandsdalen' % settings.OLD_SITE}),
    url(r'^skientelemark/$', 'page.views.redirect', kwargs={'url': 'http://www2.turistforeningen.no/skientelemark/'}),
    url(r'^skred/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=6285&fo_id=2714' % settings.OLD_SITE}),
    url(r'^smaalenene/$', 'page.views.redirect', kwargs={'url': 'http://%s/indreostfold/' % settings.OLD_SITE}),
    url(r'^sor-varanger/$', 'page.views.redirect', kwargs={'url': 'http://%s/group.php?gr_id=48&fo_id=128' % settings.OLD_SITE}),
    url(r'^sotajazz/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=8151&fo_id=2419' % settings.OLD_SITE}),
    url(r'^sotaseter2/$', 'page.views.redirect', kwargs={'url': 'http://%s/sotaseter' % settings.OLD_SITE}),
    url(r'^telenorbarn/$', 'page.views.redirect', kwargs={'url': 'http://%s/form2.php?form=telenorbarn' % settings.OLD_SITE}),
    url(r'^tester/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=2771' % settings.OLD_SITE}),
    url(r'^tromsturlag/$', 'page.views.redirect', kwargs={'url': 'http://%s/troms/' % settings.OLD_SITE}),
    url(r'^turbosvar/$', 'page.views.redirect', kwargs={'url': 'http://response.questback.com/dennorsketuristforening/ud57ujnxnk/'}),
    url(r'^varanger/$', 'page.views.redirect', kwargs={'url': 'http://%s/group.php?gr_id=51&fo_id=128' % settings.OLD_SITE}),
    url(r'^verving/$', 'page.views.redirect', kwargs={'url': 'http://%s/form2.php?form=verving' % settings.OLD_SITE}),
    url(r'^skredkurs/$', 'page.views.redirect', kwargs={'url': 'http://%s/activity.php?ac_cat=skredkurs&fo_id=9024' % settings.OLD_SITE}),
    url(r'^telemark/ung/$', 'page.views.redirect', kwargs={'url': 'http://www.dntung.no/telemark/'}),
    url(r'^troms/barn/$', 'page.views.redirect', kwargs={'url': 'http://%s/troms/group.php?gr_id=183' % settings.OLD_SITE}),
    url(r'^aot/$', 'page.views.redirect', kwargs={'url': 'http://%s/aust-agder' % settings.OLD_SITE}),
    url(r'^harstad/$', 'page.views.redirect', kwargs={'url': 'http://www.harstad-turlag.no'}),
    url(r'^matogreise/$', 'page.views.redirect', kwargs={'url': 'http://www.matogreiseliv.no'}),
    url(r'^stavanger/$', 'page.views.redirect', kwargs={'url': 'http://www.stavanger-turistforening.no'}),
    url(r'^preikestolhytta/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/preikestolenfjellstue'}),
    url(r'^francaise/$', 'page.views.redirect', kwargs={'url': 'http://%s/francais/' % settings.OLD_SITE}),
    url(r'^sot/$', 'page.views.redirect', kwargs={'url': 'http://%s/sulitjelma' % settings.OLD_SITE}),
    url(r'^kartbutikken/$', 'page.views.redirect', kwargs={'url': 'http://www.nettbutikken.dntoslo.no/eshop'}),
    url(r'^gtt/$', 'page.views.redirect', kwargs={'url': 'http://%s/gjovik' % settings.OLD_SITE}),
    url(r'^kartbutikk/$', 'page.views.redirect', kwargs={'url': 'http://www.nettbutikken.dntoslo.no/eshop/main.aspx?guest=yes'}),
    url(r'^skolecamp/$', 'page.views.redirect', kwargs={'url': 'http://www.skolecamp.no/'}),
    url(r'^httur/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/haugesund'}),
    url(r'^buss/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/article.php?ar_id=10549&fo_id=311'}),
    url(r'^fotokonkurranse/$', 'page.views.redirect', kwargs={'url': 'http://%s/form2.php?form=fotokonkurranse' % settings.OLD_SITE}),
    url(r'^fredrikstad/$', 'page.views.redirect', kwargs={'url': 'http://%s/nedreglomma' % settings.OLD_SITE}),
    url(r'^engerdalogtrysil/$', 'page.views.redirect', kwargs={'url': 'http://%s/group.php?gr_id=16&fo_id=128' % settings.OLD_SITE}),
    url(r'^aat/$', 'page.views.redirect', kwargs={'url': 'http://%s/aust-agder' % settings.OLD_SITE}),
    url(r'^medlemsfordeler/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=3814' % settings.OLD_SITE}),
    url(r'^girofeil/$', 'page.views.redirect', kwargs={'url': 'http://%s/article.php?ar_id=25749&fo_id=15' % settings.OLD_SITE}),
    url(r'^donald/$', 'page.views.redirect', kwargs={'url': 'http://innmelding.turistforeningen.no'}),
    url(r'^komdegut/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/komdegut/index.php'}),
    url(r'^bcp/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/preikestolen_basecamp'}),
    url(r'^preikestolenbasecamp/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/preikestolen_basecamp'}),
    url(r'^singeltur/$', 'page.views.redirect', kwargs={'url': 'http://%s/activity.php?fo_id=2513&search_string=&ac_cat=singeltur' % settings.OLD_SITE}),
    url(r'^snoheim/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/snøheim'}),
    url(r'^blogg/$', 'page.views.redirect', kwargs={'url': 'http://blogg.turistforeningen.no/'}),
    url(r'^go/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/gjovik'}),
    url(r'^sykkelturforslag/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/sykkelturforslag/index.php'}),
    url(r'^strandalshytta/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/stranddalshytta'}),
    url(r'^fyr/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/article.php?ar_id=27945'}),
    url(r'^yst/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/ytresogn'}),
    url(r'^hyttefoto/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/form2.php?form=hyttebilder'}),
    url(r'^era2012/$', 'page.views.redirect', kwargs={'url': 'http://www.turistforeningen.no/english/form2.php?form=era12'}),
    url(r'^gullnokkel/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=9786' % settings.OLD_SITE}),
    url(r'^gullgjest/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=9786' % settings.OLD_SITE}),
    url(r'^hyttesamler/$', 'page.views.redirect', kwargs={'url': 'http://%s/index.php?fo_id=9786' % settings.OLD_SITE}),
    url(r'^kitekurs/$', 'page.views.redirect', kwargs={'url': 'http://%s/activity.php?ac_cat=kiting&fo_id=9893' % settings.OLD_SITE}),
    url(r'^preikestolenfjellstue/$', 'page.views.redirect', kwargs={'url': 'http://www.preikestolenfjellstue.no'}),
)
