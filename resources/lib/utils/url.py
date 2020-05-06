import sys
if sys.version_info >= (3, 0, 0,):
    from urllib.parse import urlparse, urlencode, quote_plus, unquote_plus
else:
    from urlparse import urlparse
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
        return url.split('?', 1)[0]
