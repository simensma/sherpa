# encoding: utf-8

def get_member_data(profile):
    if not profile.is_member():
        return {
            'sherpa_id': profile.id,
            'er_medlem': False,
            'fornavn': profile.get_first_name(),
            'etternavn': profile.get_last_name(),
            'epost': profile.get_email()
        }
    else:
        # The gender definition is in norwegian
        def api_gender_output(gender):
            if gender == 'm':
                return 'M'
            elif gender == 'f':
                return 'K'

        address = profile.get_actor().get_clean_address()
        return {
            'sherpa_id': profile.id,
            'er_medlem': True,
            'medlemsnummer': profile.memberid,
            'aktivt_medlemskap': profile.get_actor().has_paid(),
            'etternavn': profile.get_last_name(),
            'fornavn': profile.get_first_name(),
            'etternavn': profile.get_last_name(),
            'født': profile.get_actor().birth_date.strftime("%Y-%m-%d"),
            'kjønn': api_gender_output(profile.get_actor().get_gender()),
            'epost': profile.get_email(),
            'mobil': profile.get_actor().phone_mobile,
            'address': {
                'adresse1': address.field1,
                'adresse2': address.field2,
                'adresse3': address.field3,
                'postnummer': address.zipcode.zipcode if address.country.code == 'NO' else None,
                'poststed': address.zipcode.area.title() if address.country.code == 'NO' else None,
                'land': {
                    'kode': address.country.code,
                    'navn': address.country.name
                }
            }
        }
