from resources.lib.api.api import API
from resources.lib.api.cached_api import CachedAPI
from resources.lib.const import SETTINGS, URL
from resources.lib.provider import provider
from resources.lib.router import Router
from resources.lib.settings import get_uuid
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_info


class Defaults:
    @staticmethod
    def provider():
        return provider(storage.dynamic(SETTINGS.PROVIDER_USERNAME),
                        storage.dynamic(SETTINGS.PROVIDER_PASSWORD),
                        storage.dynamic(SETTINGS.PROVIDER_TOKEN))

    @staticmethod
    def router():
        return Router()

    @staticmethod
    def api():
        return API(
            plugin_version=get_info('version'),
            uuid=get_uuid(),
            api_url=URL.API
        )

    @staticmethod
    def api_cached():
        return CachedAPI(
            'main',
            plugin_version=get_info('version'),
            uuid=get_uuid(),
            api_url=URL.API
        )
