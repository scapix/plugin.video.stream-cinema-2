"""
    # Main routing to go through different menu screens. 
"""
import logging
import sys

import xbmc
import uuid
from resources.lib.cache import PluginUrlHistory
from resources.lib.const import SETTINGS, ROUTE
from resources.lib.defaults import Defaults
from resources.lib import kodilogging
from resources.lib.kodilogging import logger, setup_root_logger
from resources.lib.settings import settings
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import get_plugin_route, go_to_plugin_url, get_plugin_url, set_resolved_url

provider = Defaults.provider()
api = Defaults.api_cached()
router = Defaults.router()
plugin_url_history = PluginUrlHistory()
stream_cinema = StreamCinema(provider, api, router)


@router.route('/')
def index():
    return stream_cinema.directory_renderer.main_menu()


def run():
    first_run()
    setup_root_logger()
    logger.debug('Entry point ------- ' + str(sys.argv))
    plugin_url_history.add(get_plugin_url())
    return router.run()


def first_run():
    if settings[SETTINGS.UUID] == '':
        settings[SETTINGS.UUID] = uuid.uuid4()
