# encoding: utf-8
import base64

from django.conf import settings

from exceptions import BadRequest
from urls import supported_versions
import error_codes

vendor_media_type = 'vnd.turistforeningen'
supported_formats = ['json']

def get_member_data(user):
    if not user.is_member():
        return {
            'sherpa_id': user.id,
            'er_medlem': False,
            'fornavn': user.get_first_name(),
            'etternavn': user.get_last_name(),
            'epost': user.get_email()
        }
    else:
        # The gender definition is in norwegian
        def api_gender_output(gender):
            if gender == 'm':
                return 'M'
            elif gender == 'f':
                return 'K'

        address = user.get_address()
        dob = user.get_birth_date()
        if dob is not None:
            dob = dob.strftime("%Y-%m-%d")

        if not user.has_perm('sherpa'):
            forening_permissions = []
        else:
            forening_permissions = [{
                'sherpa_id': f.id,
                'object_id': f.get_ntb_id(),
            } for f in user.all_foreninger()]

        return {
            'sherpa_id': user.id,
            'er_medlem': True,
            'medlemsnummer': user.memberid,
            'forening': {'sherpa_id': user.main_forening().id, 'navn': user.main_forening().name},
            'aktivt_medlemskap': user.has_paid(),
            'fornavn': user.get_first_name(),
            'etternavn': user.get_last_name(),
            'født': dob,
            'kjønn': api_gender_output(user.get_gender()),
            'epost': user.get_email(),
            'mobil': user.get_phone_mobile(),
            'adresse': {
                'adresse1': address.field1,
                'adresse2': address.field2,
                'adresse3': address.field3,
                'postnummer': address.zipcode.zipcode if address.country.code == 'NO' else None,
                'poststed': address.zipcode.area.title() if address.country.code == 'NO' else None,
                'land': {
                    'kode': address.country.code,
                    'navn': address.country.name
                }
            },
            'foreningstilganger': forening_permissions,
        }

def get_forening_data(forening):
    return {
        'sherpa_id': forening.id,
        'object_id': forening.get_ntb_id(),
        'navn': forening.name,
        'type': forening.type,
        'gruppetype': forening.group_type,
    }

def authenticate(request):
    try:
        return base64.b64decode(request.GET.get('autentisering', '')) in settings.API_KEYS
    except (TypeError, UnicodeEncodeError):
        raise BadRequest(
            "Unable to base64-decode your authentication parameter '%s'" % request.GET.get('autentisering', ''),
            code=error_codes.INVALID_AUTHENTICATION,
            http_code=400
        )

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

def require_focus(request):
    if not request.db_connections['focus']['is_available']:
        raise BadRequest(
            "Our member system is required by this API call, however it is currently down for maintenance.",
            code=error_codes.FOCUS_IS_DOWN,
            http_code=500
        )
