import base64
import json
import sys
if sys.version_info >= (3, 0, 0,):
    from urllib.parse import urlparse, urlencode, quote_plus, unquote_plus, unquote, quote
else:
    from urlparse import urlparse
    from urllib import urlencode, quote_plus, unquote_plus, unquote, quote


class Url:
    @staticmethod
    def parse(*args, **kwargs):
        return urlparse(*args, **kwargs)

    @staticmethod
    def encode(*args, **kwargs):
        return urlencode(*args, **kwargs)

    @staticmethod
    def quote(*args, **kwargs):
        return quote(*args, **kwargs)

    @staticmethod
    def unquote(*args, **kwargs):
        return unquote(*args, **kwargs)

    @staticmethod
    def quote_plus(*args, **kwargs):
        return quote_plus(*args, **kwargs)

    @staticmethod
    def unquote_plus(*args, **kwargs):
        return unquote_plus(*args, **kwargs)

    @staticmethod
    def remove_params(url):
        return url.split('?', 1)[0]

    @staticmethod
    def encode_param(data):
        return base64.b64encode(json.dumps(data))

    @staticmethod
    def decode_param(data):
        return json.loads(base64.b64decode(data))
