"""
    # Main routing to go through different menu screens. 
"""
import os
import sys
import uuid
from datetime import datetime

import requests

from resources.lib.api.gitlab_api import GitLabAPI
from resources.lib.const import SETTINGS, RENDERER, LANG, STORAGE, ROUTE, GENERAL
from resources.lib.defaults import Defaults
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger, setup_root_logger
from resources.lib.plugin_url_history import PluginUrlHistory
from resources.lib.settings import settings
from resources.lib.storage.storage import storage
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import get_plugin_url, get_string, get_settings, \
    set_settings, get_current_datetime_str, get_setting_as_datetime, datetime_from_iso

provider = Defaults.provider()
api = Defaults.api_cached()
gitlab_api = GitLabAPI()
router = Defaults.router()
plugin_url_history = PluginUrlHistory()
stream_cinema = StreamCinema(provider, api, router)


@router.route('/')
def index():
    return stream_cinema.renderers[RENDERER.DIRECTORIES].main_menu()


def run():
    first_run()
    setup_root_logger()
    on_clear_cache_redirect()
    logger.debug('Entry point ------- ' + str(sys.argv))
    check_version()
    plugin_url_history.add(get_plugin_url())
    return router.run()


def first_run():
    if settings[SETTINGS.UUID] == '':
        settings[SETTINGS.UUID] = uuid.uuid4()
        DialogRenderer.ok(get_string(LANG.NEWS_TITLE), get_string(LANG.NEWS_TEXT))
    if settings[SETTINGS.INSTALLATION_DATE] == '':
        set_settings(SETTINGS.INSTALLATION_DATE, get_current_datetime_str())


@router.route('/clear-cache')
def clear_cache():
    del storage[STORAGE.MEDIA_LIST]
    del storage[STORAGE.COLLECTION]
    del storage[STORAGE.PLUGIN_URL_HISTORY]
    del storage[STORAGE.PLUGIN_LAST_URL_ADDED]
    del storage[STORAGE.SERVICE]
    storage[STORAGE.CLEARED_CACHE] = True


def on_clear_cache_redirect():
    if storage.get(STORAGE.CLEARED_CACHE):
        logger.debug('Cache is empty. Redirecting to main menu')
        storage[STORAGE.CLEARED_CACHE] = False
        router.replace_route(ROUTE.MAIN_MENU)


def can_do_version_check():
    last_version_check = get_setting_as_datetime(SETTINGS.LAST_VERSION_CHECK)
    current_datetime = datetime.now()
    if last_version_check is None:
        return True
    return current_datetime - GENERAL.VERSION_CHECK_INTERVAL > last_version_check


def check_version():
    if can_do_version_check():
        set_settings(SETTINGS.LAST_VERSION_CHECK, datetime.now())
        releases = gitlab_api.get_latest_release()
        latest_release_at = max(releases, key=lambda x: datetime_from_iso(x['released_at'])).get('released_at')
        if latest_release_at:
            latest_release_at = datetime_from_iso(latest_release_at)
            installation_date = get_setting_as_datetime(SETTINGS.INSTALLATION_DATE)
            if latest_release_at > installation_date:
                DialogRenderer.ok(get_string(LANG.NEW_VERSION_TITLE), get_string(LANG.NEW_VERSION_TEXT))


