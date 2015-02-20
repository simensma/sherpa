# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def add_initial_stf_prices(apps, schema_editor):
    Forening = apps.get_model("foreninger", "Forening")
    SupplyCategory = apps.get_model("foreninger", "SupplyCategory")
    Supply = apps.get_model("foreninger", "Supply")
    Lodging = apps.get_model("foreninger", "Lodging")

    stf = Forening.objects.get(name="Stavanger Turistforening")

    # Define supply categories

    middag = SupplyCategory(forening=stf, name="Middag")
    middag.save()

    middagstilbehor = SupplyCategory(forening=stf, name="Middagstilbehør")
    middagstilbehor.save()

    dessert = SupplyCategory(forening=stf, name="Dessert")
    dessert.save()

    annet = SupplyCategory(forening=stf, name="Annet")
    annet.save()

    supper_og_drikke = SupplyCategory(forening=stf, name="Supper og drikke")
    supper_og_drikke.save()

    frokostprodukter_og_kjeks = SupplyCategory(forening=stf, name="Frokostprodukter og kjeks")
    frokostprodukter_og_kjeks.save()

    # Define supply prices

    Supply(
        supply_category=middag,
        name='Kjøttkaker',
        price_member=82,
        price_nonmember=88,
    ).save()

    Supply(
        supply_category=middag,
        name='Pasta Parma',
        price_member=44,
        price_nonmember=48,
    ).save()

    Supply(
        supply_category=middag,
        name='Turistproviant',
        price_member=50,
        price_nonmember=54,
    ).save()

    Supply(
        supply_category=middag,
        name='Bacalao',
        price_member=82,
        price_nonmember=88,
    ).save()

    Supply(
        supply_category=middag,
        name='Bogskinke',
        price_member=62,
        price_nonmember=66,
    ).save()

    Supply(
        supply_category=middag,
        name='Kjøttboller',
        price_member=62,
        price_nonmember=66,
    ).save()

    Supply(
        supply_category=middag,
        name='Lapskaus Lys',
        price_member=62,
        price_nonmember=66,
    ).save()

    Supply(
        supply_category=middag,
        name='Lapskaus Brun',
        price_member=62,
        price_nonmember=66,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Ertestuing',
        price_member=32,
        price_nonmember=36,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Spagetti, 500g',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Potetmos m/melk',
        price_member=22,
        price_nonmember=26,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Ris, 400g',
        price_member=40,
        price_nonmember=44,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Ris, boil in bag, pr. pose',
        price_member=10,
        price_nonmember=12,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Champignon, boks',
        price_member=12,
        price_nonmember=14,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Erter & gulrøtter, boks',
        price_member=18,
        price_nonmember=20,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Kjøttdeigsaus',
        price_member=24,
        price_nonmember=28,
    ).save()

    Supply(
        supply_category=middagstilbehor,
        name='Jegergryte',
        price_member=46,
        price_nonmember=50,
    ).save()

    Supply(
        supply_category=dessert,
        name='Pannekakemix',
        price_member=32,
        price_nonmember=36,
    ).save()

    Supply(
        supply_category=dessert,
        name='Fruktcocktail, 1/2',
        price_member=28,
        price_nonmember=32,
    ).save()

    Supply(
        supply_category=dessert,
        name='Fruktcocktail, 1/1',
        price_member=38,
        price_nonmember=42,
    ).save()

    Supply(
        supply_category=annet,
        name='Fyrstikker',
        price_member=2,
        price_nonmember=3,
    ).save()

    Supply(
        supply_category=annet,
        name='Stearinlys',
        price_member=3,
        price_nonmember=4,
    ).save()

    Supply(
        supply_category=annet,
        name='Plaster pr. stk.',
        price_member=2,
        price_nonmember=3,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Iste fersken',
        price_member=20,
        price_nonmember=24,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Kaffe pr. kopp',
        price_member=4,
        price_nonmember=5,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Sjokoladedrikk',
        price_member=10,
        price_nonmember=12,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Suppeposer',
        price_member=32,
        price_nonmember=36,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Solbærtoddy',
        price_member=10,
        price_nonmember=12,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Teposer pr. stk.',
        price_member=4,
        price_nonmember=5,
    ).save()

    Supply(
        supply_category=supper_og_drikke,
        name='Tørrmelk, 15g',
        price_member=4,
        price_nonmember=5,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Stabbur-Laks',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Havregryn pr. pose',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Knekkebrød pr. pk.',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Leverpostei pr. boks',
        price_member=24,
        price_nonmember=28,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Makrellfilet, tomat',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Margarin pr. kuvert',
        price_member=4,
        price_nonmember=5,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Syltetøy pr. kuvert',
        price_member=5,
        price_nonmember=6,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Bixit sjokolade',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Gjende kjeks',
        price_member=30,
        price_nonmember=34,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Honning',
        price_member=8,
        price_nonmember=10,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Wasa Sandwich',
        price_member=16,
        price_nonmember=18,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Nugatti',
        price_member=32,
        price_nonmember=36,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Rosiner pr. eske',
        price_member=20,
        price_nonmember=22,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Havregrøt porsjonspakn.',
        price_member=12,
        price_nonmember=14,
    ).save()

    Supply(
        supply_category=frokostprodukter_og_kjeks,
        name='Solsikkeolje, pr. steking',
        price_member=3,
        price_nonmember=4,
    ).save()

    # Define loding prices

    Lodging(
        name="Losji voksne",
        price_member=230,
        price_nonmember=335,
    ).save()

    Lodging(
        name="Losji 0-12 år / Barnas Turlag",
        price_member=0,
        price_nonmember=165,
    ).save()

    Lodging(
        name="Losji 13-26 år",
        price_member=115,
        price_nonmember=335,
    ).save()

    Lodging(
        name="Dagsbesøk",
        price_member=60,
        price_nonmember=75,
    ).save()

    Lodging(
        name="Dagsbesøk pr. familie",
        price_member=75,
        price_nonmember=90,
    ).save()

class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0005_auto_20150220_0934'),
    ]

    operations = [
        migrations.RunPython(add_initial_stf_prices)
    ]
