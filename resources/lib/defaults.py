from resources.lib.api import API
from resources.lib.cache import Cache, CachedAPI
from resources.lib.const import SETTINGS, URL
from resources.lib.provider import provider
from resources.lib.router import Router
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import get_info
import routing


class Defaults:
    @staticmethod
    def provider():
        return provider(settings[SETTINGS.PROVIDER_USERNAME],
                        settings[SETTINGS.PROVIDER_PASSWORD],
                        settings[SETTINGS.PROVIDER_TOKEN])

    @staticmethod
    def router():
        return Router()

    @staticmethod
    def api():
        return API(
            plugin_version=get_info('version'),
            uuid=settings[SETTINGS.UUID],
            api_url=URL.API
        )

    @staticmethod
    def api_cached():
        return CachedAPI(
            'main',
            plugin_version=get_info('version'),
            uuid=settings[SETTINGS.UUID],
            api_url=URL.API
        )


    @staticmethod
    def cache():
        return Cache(get_info('id'))

