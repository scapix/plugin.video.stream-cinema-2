from resources.lib.const import SETTINGS
from resources.lib.providers.webshare import Webshare
from resources.lib.settings import settings

select_providers = {
    '0': Webshare
}


def get_provider():
    for lang_id, p in select_providers.items():
        if lang_id == settings[SETTINGS.PROVIDER_NAME]:
            return p


provider = get_provider()
