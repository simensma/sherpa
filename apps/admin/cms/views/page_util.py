from core.models import Site
from foreninger.models import Forening

def verify_domain(domain):
    """Very simple syntax verification, and a few business rules"""
    domain = domain.strip()
    if domain == '' or domain == 'http://' or not domain.startswith('http://') or not '.' in domain:
        return {
            'valid': False,
            'error': 'malformed',
        }

    domain = domain[len('http://'):]
    if domain.endswith('/'):
        domain = domain[:-1]

    if '/' not in domain:
        prefix = ''
    else:
        try:
            # Prefix folder specified
            domain, prefix = domain.split('/')
            # Only allowed for turistforeningen.no
            if domain != 'turistforeningen.no' and domain != 'www.turistforeningen.no':
                return {
                    'valid': False,
                    'error': 'prefix_for_disallowed_domain',
                }
        except ValueError:
            # More than one subdir specified
            return {
                'valid': False,
                'error': 'more_than_one_subdir',
            }

    if prefix != '':
        return {
            'valid': False,
            'error': 'prefix_not_supported_yet',
        }

    if domain.count('.') == 1 and not domain.startswith('www'):
        domain = "www.%s" % domain

    try:
        existing_site = Site.objects.get(domain=domain, prefix=prefix)
        existing_forening = Forening.objects.get(site=existing_site)
        return {
            'valid': False,
            'error': 'site_exists',
            'existing_forening': existing_forening,
        }
    except Site.DoesNotExist:
        pass

    return {
        'valid': True,
        'domain': domain,
        'prefix': prefix,
    }
