# encoding: utf-8

from django.conf import settings

import base64

from exceptions import BadRequest
import error_codes

vendor_media_type = 'vnd.turistforeningen'
supported_formats = ['json']
supported_versions = ['v0']

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

def authenticate(request):
    return base64.b64decode(request.GET.get('autentisering', '')) in settings.API_KEYS

def requested_representation_from_header(request):
    accepted_types = request.META.get('HTTP_ACCEPT', '').split(',')
    valid_types = []
    for t in accepted_types:
        type, subtype = [v.strip() for v in t.split('/')]

        # Skip other media types
        if type != 'application' or not subtype.startswith(vendor_media_type):
            continue

        # Format specified?
        if '+' in subtype:
            subtype, format = subtype.split('+')
            if not format in supported_formats:
                raise BadRequest(
                    "The requested representation format '%s' is not one of the following supported formats: %s" % (format, ', '.join(supported_formats)),
                    code=error_codes.INVALID_REPRESENTATION,
                    http_code=400
                )
        else:
            # No format specified, default to the first item
            format = supported_formats[0]

        if subtype == vendor_media_type:
            # No version specified, default to the last item
            version = supported_versions[len(supported_versions) - 1]
        else:
            subtype, version = subtype.rsplit('.', 1)

        if version not in supported_versions:
            print("NOT SUPPORTING %s" % version)
            # Unsupported version, skip
            continue

        valid_types.append({
            'version': version,
            'format': format,
        })

    if len(valid_types) == 0:
        raise BadRequest(
            "You need to accept one of the following API versions in your media type: %s" % ', '.join(supported_versions),
            code=error_codes.INVALID_REPRESENTATION,
            http_code=400
        )

    preferred_version = max(valid_types, key=lambda v: int(v['version'][1]))
    return preferred_version['version'], preferred_version['format']

def requested_representation_from_url(request):
    format = request.GET.get('format', supported_formats[0])
    if not format in supported_formats:
        raise BadRequest(
            "The requested representation format '%s' is not one of the following supported formats: %s" % (format, ', '.join(supported_formats)),
            code=error_codes.INVALID_REPRESENTATION,
            http_code=400
        )
    return format

def invalid_authentication_exception():
    return BadRequest(
        "Invalid authentication",
        code=error_codes.INVALID_AUTHENTICATION,
        http_code=403
    )

def invalid_version_response(version):
    return BadRequest(
        "The API version '%s' does not provide the requested resource" % version,
        code=error_codes.INVALID_REPRESENTATION,
        http_code=400
    ).response()
