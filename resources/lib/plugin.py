"""
    # Main routing to go through different menu screens. 
"""
import os
import sys
import uuid
from datetime import datetime
import requests
import xbmc
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
    set_settings, get_current_datetime_str, get_setting_as_datetime, datetime_from_iso, get_info, apply_strings, \
    time_limit_expired

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

    if not storage.get(STORAGE.IS_OLD_KODI_SESSION):
        storage[STORAGE.IS_OLD_KODI_SESSION] = True
        load_settings()


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
    xbmc.executebuiltin('Container.Refresh')
    if stream_cinema.ensure_provider_token():
        InfoDialog(get_string(LANG.CORRECT_PROVIDER_CREDENTIALS), sound=True).notify()


@router.route(ROUTE.REFRESH_PROVIDER_TOKEN)
def refresh_provider_token():
    stream_cinema.ensure_provider_token()
    DialogRenderer.ok(get_string(LANG.INFO), get_string(LANG.TOKEN_REFRESHED))


@router.route(ROUTE.SET_PROVIDER_CREDENTIALS)
def set_provider_credentials():
    username = DialogRenderer.keyboard(get_string(LANG.USERNAME))
    password = DialogRenderer.keyboard(get_string(LANG.PASSWORD), hidden=True)

    if username:
        settings.set_cache(SETTINGS.PROVIDER_USERNAME, username)
        settings.set_cache(SETTINGS.PROVIDER_TOKEN, '')
    if password:
        settings.set_cache(SETTINGS.PROVIDER_PASSWORD, password)


def load_settings():
    settings.load_to_cache(SETTINGS.PROVIDER_USERNAME, SETTINGS.PROVIDER_PASSWORD, SETTINGS.PROVIDER_TOKEN)


def on_clear_cache_redirect():
    if storage.get(STORAGE.CLEARED_CACHE):
        logger.debug('Cache is empty. Redirecting to main menu')
        storage[STORAGE.CLEARED_CACHE] = False
        router.replace_route(ROUTE.ROOT)


def check_version():
    if time_limit_expired(SETTINGS.LAST_VERSION_CHECK,
                          GENERAL.VERSION_CHECK_INTERVAL) or settings[SETTINGS.LAST_VERSION_AVAILABLE] == '':
        settings[SETTINGS.LAST_VERSION_CHECK] = datetime.now()
        tag_name = get_latest_release_tag_name()
        if tag_name:
            settings[SETTINGS.LAST_VERSION_AVAILABLE] = apply_strings(tag_name, STRINGS.BOLD, STRINGS.COLOR_GREEN)
            current_version = settings[SETTINGS.VERSION]
            if current_version != tag_name:
                settings[SETTINGS.IS_OUTDATED] = True
                DialogRenderer.ok(get_string(LANG.NEW_VERSION_TITLE),
                                  get_string(LANG.NEW_VERSION_TEXT).format(version=tag_name))
            else:
                settings[SETTINGS.IS_OUTDATED] = False


def get_latest_release_tag_name():
    releases = gitlab_api.get_latest_release()
    latest_release = max(releases, key=lambda x: datetime_from_iso(x['released_at']))
    if latest_release:
        return latest_release.get('tag_name')
