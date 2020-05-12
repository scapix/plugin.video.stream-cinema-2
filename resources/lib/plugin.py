"""
    # Main routing to go through different menu screens. 
"""
import os
import sys
import uuid
from datetime import datetime
import requests
from xbmcgui import DialogBusy, DialogProgress

from resources.lib.api.gitlab_api import GitLabAPI
from resources.lib.const import SETTINGS, RENDERER, LANG, STORAGE, ROUTE, GENERAL, STRINGS
from resources.lib.defaults import Defaults
from resources.lib.gui import InfoDialog
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.text_renderer import TextRenderer
from resources.lib.kodilogging import logger, setup_root_logger
from resources.lib.plugin_url_history import PluginUrlHistory
from resources.lib.providers.webshare import plugin
from resources.lib.settings import settings
from resources.lib.storage.storage import storage
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import get_plugin_url, get_string, get_settings, \
    set_settings, get_current_datetime_str, get_setting_as_datetime, datetime_from_iso, get_info, apply_strings

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
    set_settings(SETTINGS.VERSION, get_info('version'))
    logger.debug('Entry point ------- ' + str(sys.argv))
    credentials_check()
    stream_cinema.vip_remains()
    check_version()
    plugin_url_history.add(get_plugin_url())
    return router.run()


def first_run():
    if settings[SETTINGS.UUID] == '':
        settings[SETTINGS.UUID] = uuid.uuid4()
        DialogRenderer.ok(get_string(LANG.NEWS_TITLE), get_string(LANG.NEWS_TEXT))
    if settings[SETTINGS.INSTALLATION_DATE] == '':
        set_settings(SETTINGS.INSTALLATION_DATE, get_current_datetime_str())
    if settings[SETTINGS.VERSION] == '':
        set_settings(SETTINGS.VERSION, get_info('version'))


@router.route(ROUTE.CLEAR_CACHE)
def clear_cache():
    del storage[STORAGE.MEDIA_LIST]
    del storage[STORAGE.COLLECTION]
    del storage[STORAGE.PLUGIN_URL_HISTORY]
    del storage[STORAGE.PLUGIN_LAST_URL_ADDED]
    del storage[STORAGE.SERVICE]
    storage[STORAGE.CLEARED_CACHE] = True


@router.route(ROUTE.CHECK_PROVIDER_CREDENTIALS)
def check_provider_credentials():
    if stream_cinema.ensure_provider_token():
        InfoDialog(get_string(LANG.CORRECT_PROVIDER_CREDENTIALS), sound=True).notify()


@router.route(ROUTE.REFRESH_PROVIDER_TOKEN)
def refresh_provider_token():
    stream_cinema.ensure_provider_token()
    DialogRenderer.ok(get_string(LANG.INFO), get_string(LANG.TOKEN_REFRESHED))


def on_clear_cache_redirect():
    if storage.get(STORAGE.CLEARED_CACHE):
        logger.debug('Cache is empty. Redirecting to main menu')
        storage[STORAGE.CLEARED_CACHE] = False
        router.replace_route(ROUTE.ROOT)


def can_do_version_check():
    last_version_check = get_setting_as_datetime(SETTINGS.LAST_VERSION_CHECK)
    current_datetime = datetime.now()
    if last_version_check is None:
        return True
    return current_datetime - GENERAL.VERSION_CHECK_INTERVAL > last_version_check


def check_version():
    if can_do_version_check() or settings[SETTINGS.LAST_VERSION_AVAILABLE] == '':
        set_settings(SETTINGS.LAST_VERSION_CHECK, datetime.now())
        tag_name = get_latest_release_tag_name()
        if tag_name:
            set_settings(SETTINGS.LAST_VERSION_AVAILABLE, STRINGS.COLOR_GREEN.format(STRINGS.BOLD.format(tag_name)))
            current_version = get_settings(SETTINGS.VERSION)
            if current_version != tag_name:
                set_settings(SETTINGS.IS_OUTDATED, True)
                DialogRenderer.ok(get_string(LANG.NEW_VERSION_TITLE),
                                  get_string(LANG.NEW_VERSION_TEXT).format(version=tag_name))
            else:
                set_settings(SETTINGS.IS_OUTDATED, False)


def get_latest_release_tag_name():
    releases = gitlab_api.get_latest_release()
    latest_release = max(releases, key=lambda x: datetime_from_iso(x['released_at']))

    if latest_release:
        return latest_release.get('tag_name')


def credentials_check():
    username = settings[SETTINGS.PROVIDER_USERNAME]
    password = settings[SETTINGS.PROVIDER_PASSWORD]
    with plugin.get_storage() as sql_storage:
        cached_username = sql_storage.get(STORAGE.PROVIDER_USERNAME)
        cached_password = sql_storage.get(STORAGE.PROVIDER_PASSWORD)
        sql_storage[STORAGE.PROVIDER_USERNAME] = username
        sql_storage[STORAGE.PROVIDER_PASSWORD] = password

        if cached_username != username or cached_password != password:
            set_settings(SETTINGS.PROVIDER_TOKEN, '')
