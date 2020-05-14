from resources.lib.providers.webshare import Webshare

select_providers = {
    '0': Webshare
}


def get_provider():
    for lang_id, p in select_providers.items():
        return p


provider = get_provider()
