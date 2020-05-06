import sys
if sys.version_info >= (3, 0, 0,):
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse, quote_plus, unquote_plus
else:
    from urlparse import urlparse, parse_qs, urlunparse
    from urllib import urlencode, quote_plus, unquote_plus


class Url:
    @staticmethod
    def parse(*args, **kwargs):
        return urlparse(*args, **kwargs)

    @staticmethod
    def encode(*args, **kwargs):
        return urlencode(*args, **kwargs)

    @staticmethod
    def quote_plus(*args, **kwargs):
        return quote_plus(*args, **kwargs)

    @staticmethod
    def unquote_plus(*args, **kwargs):
        return unquote_plus(*args, **kwargs)

    @staticmethod
    def remove_params(url):
        uu = list(urlparse(url))
        qs = parse_qs(uu[4], keep_blank_values=True)
        if 'q2' in qs:
            del (qs['q2'])
        uu[4] = urlencode(qs, doseq=True)
        return urlunparse(uu)
