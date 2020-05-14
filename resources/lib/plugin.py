"""
    # Main routing to go through different menu screens.
"""
import sys
import uuid
import requests
from datetime import datetime
from resources.lib.api.gitlab_api import GitLabAPI
from resources.lib.const import SETTINGS, RENDERER, LANG, STORAGE, ROUTE, GENERAL
from resources.lib.defaults import Defaults
from resources.lib.gui import InfoDialog
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger, setup_root_logger
from resources.lib.plugin_url_history import PluginUrlHistory
from resources.lib.settings import settings
from resources.lib.storage.storage import storage
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import get_plugin_url, get_string, get_current_datetime_str, \
    datetime_from_iso, get_info, time_limit_expired, clear_kodi_addon_cache, get_plugin_route
import socket
from xbmcgui import Dialog

provider = Defaults.provider()
api = Defaults.api()
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
    settings.set_cache(SETTINGS.VERSION, get_info('version'))
    logger.debug('Entry point ------- ' + str(sys.argv))
    try:
        stream_cinema.vip_remains()
        # settings.load_to_cache(SETTINGS.PROVIDER_USERNAME, SETTINGS.PROVIDER_PASSWORD, SETTINGS.PROVIDER_TOKEN)
        check_version()
        plugin_url_history.add(get_plugin_url())
        return router.run()
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        if _can_connect_google():
            Dialog().ok(get_string(LANG.CONNECTION_ERROR), get_string(LANG.SERVER_ERROR_HELP))
        else:
            Dialog().ok(get_string(LANG.CONNECTION_ERROR), get_string(LANG.NO_CONNECTION_HELP))


def first_run():
    if settings[SETTINGS.UUID] == '':
        settings.set_cache(SETTINGS.UUID, uuid.uuid4())
        DialogRenderer.ok(get_string(LANG.NEWS_TITLE), get_string(LANG.NEWS_TEXT))
    if settings[SETTINGS.INSTALLATION_DATE] == '':
        settings.set_cache(SETTINGS.INSTALLATION_DATE, get_current_datetime_str())
    if settings[SETTINGS.VERSION] == '':
        settings.set_cache(SETTINGS.VERSION, get_info('version'))

    if settings[SETTINGS.PROVIDER_USERNAME] == '':
        settings.set_cache(SETTINGS.PROVIDER_TOKEN, '')

    if get_plugin_route() != ROUTE.CHECK_PROVIDER_CREDENTIALS or not storage.get(STORAGE.IS_OLD_KODI_SESSION):
        settings.load_to_cache(SETTINGS.PROVIDER_NAME, SETTINGS.PROVIDER_USERNAME, SETTINGS.PROVIDER_PASSWORD, SETTINGS.PROVIDER_TOKEN)

    if not storage.get(STORAGE.IS_OLD_KODI_SESSION):
        storage[STORAGE.IS_OLD_KODI_SESSION] = True


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
    if stream_cinema.ensure_provider_token():
        DialogRenderer.ok(get_string(LANG.INFO), get_string(LANG.TOKEN_REFRESHED))


@router.route(ROUTE.SET_PROVIDER_CREDENTIALS)
def set_provider_credentials():
    oldusername = settings[SETTINGS.PROVIDER_USERNAME]
    username = DialogRenderer.keyboard(get_string(LANG.USERNAME), oldusername)

    if not oldusername and not username:
        return

    if username:
        password = DialogRenderer.keyboard(get_string(LANG.PASSWORD), '', True)
        if password:
            settings.set_cache(SETTINGS.PROVIDER_USERNAME, username)
            settings.set_cache(SETTINGS.PROVIDER_PASSWORD, password)
            settings.set_cache(SETTINGS.PROVIDER_TOKEN, '')
            settings.set_cache(SETTINGS.VIP_DURATION, '')
            logger.debug('Saving credentials to cache')
            if stream_cinema.ensure_provider_token():
                InfoDialog(get_string(LANG.CORRECT_PROVIDER_CREDENTIALS), sound=True).notify()
    else:
        stream_cinema.logout()


def on_clear_cache_redirect():
    if storage.get(STORAGE.CLEARED_CACHE):
        logger.debug('Cache is empty. Redirecting to main menu')
        storage[STORAGE.CLEARED_CACHE] = False
        router.replace_route(ROUTE.ROOT)


def check_version():
    if time_limit_expired(SETTINGS.LAST_VERSION_CHECK,
                          GENERAL.VERSION_CHECK_INTERVAL) or settings[SETTINGS.LAST_VERSION_AVAILABLE] == '':
        settings.set_cache(SETTINGS.LAST_VERSION_CHECK, datetime.now())
        tag_name = get_latest_release_tag_name()
        if tag_name:
            settings.set_cache(SETTINGS.LAST_VERSION_AVAILABLE, tag_name)
            current_version = settings[SETTINGS.VERSION]
            if current_version != tag_name:
                settings.set_cache(SETTINGS.IS_OUTDATED, True)
                clear_kodi_addon_cache()
                DialogRenderer.ok(get_string(LANG.NEW_VERSION_TITLE),
                                  get_string(LANG.NEW_VERSION_TEXT).format(version=tag_name))
            else:
                settings.set_cache(SETTINGS.IS_OUTDATED, False)


def get_latest_release_tag_name():
    releases = gitlab_api.get_latest_release()
    latest_release = max(releases, key=lambda x: datetime_from_iso(x['released_at']))
    if latest_release:
        return latest_release.get('tag_name')

def _can_connect_google():
    google_addr = ("www.google.com", 443)
    soc = None
    try:
        soc = socket.create_connection(google_addr)
        return True
    except Exception as e:
        logger.debug("failed to connect to %s: %s", google_addr, e)
        return False
    finally:
        if soc is not None:
            soc.close()
