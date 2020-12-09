from django.urls import (
    set_urlconf,
    get_urlconf
)
from django.conf import settings


def subdomain_middleware(get_response):
    def middleware(request):
        split_domains = request.get_host().split(":")[0].split(".")
        subdomain = None if len(split_domains) < 3 else split_domains[0]

        if subdomain not in settings.SUBDOMAIN_USE_ROOT:
            old_urlconf = get_urlconf()

            try:
                set_urlconf(settings.SUBDOMAIN_URLCONF)
                request.urlconf = settings.SUBDOMAIN_URLCONF
                request.META["subdomain"] = subdomain

                return get_response(request)
            finally:
                set_urlconf(old_urlconf)
                request.urlconf = old_urlconf
        else:
            return get_response(request)

    return middleware
