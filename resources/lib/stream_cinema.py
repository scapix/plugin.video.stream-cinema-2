"""
    Main GUI.
"""

import contextlib

import requests
import xbmc
import xbmcgui
import xbmcplugin
from xbmcgui import Dialog
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem
from xbmcplugin import endOfDirectory

from resources.lib.cache import PluginUrlHistory
from resources.lib.const import COMMAND, CACHE, SETTINGS, FILTER_TYPE, STRINGS, ROUTE
from resources.lib.gui import DirectoryItem, InfoDialog, SettingsItem, InfoDialogType, MediaItem, FolderBackItem
from resources.lib.gui import MoviesItem
from resources.lib.gui import SearchItem
from resources.lib.gui import SeriesItem
from resources.lib.gui.renderers.dialog import DialogRenderer
from resources.lib.gui.renderers.directory import DirectoryRenderer
from resources.lib.gui.renderers.media_list import MediaListRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import show_settings, get_string, show_input, get_plugin_base_url, \
    go_to_plugin_url, set_resolved_url, router_url_for
from resources.lib.utils.url import Url


class StreamCinema:
    def __init__(self, provider, api, router=None):
        self._api = api
        self._router = router
        self._provider = provider
        self.directory_renderer = DirectoryRenderer(router)
        self.media_list_renderer = MediaListRenderer(router, on_stream_selected=self.play_stream)

        router.add_route(self.media_list_renderer.select_stream, ROUTE.SELECT_STREAM)
        router.add_route(self.directory_renderer.search, ROUTE.SEARCH)
        router.add_route(self.directory_renderer.main_menu, ROUTE.MAIN_MENU)
        router.add_route(self.directory_renderer.media_menu, ROUTE.MEDIA_MENU)
        router.add_route(self.directory_renderer.command, ROUTE.COMMAND)
        router.add_route(self.directory_renderer.a_to_z_menu, ROUTE.A_TO_Z)
        router.add_route(self.next_page, ROUTE.NEXT_PAGE)
        router.add_route(self.search_result, ROUTE.SEARCH_RESULT)
        router.add_route(self.filter, ROUTE.FILTER)
        self._check_token()

    @property
    def router(self):
        return self._router

    def _filter_and_render(self, collection, filter_type, filter_value):
        media = self.filter_media(collection, filter_type, filter_value)
        self.show_search_results(collection, media)

    def next_page(self, collection, url):
        url = Url.unquote_plus(url)
        media = self.get_media(self._api.next_page(url))
        self.render_media_list(media, collection)

    def filter(self, collection, filter_type, filter_value):
        self._filter_and_render(collection, filter_type, filter_value)

    def search_result(self, collection, search_value):
        self.filter(collection, FILTER_TYPE.TITLE_OR_ACTOR, search_value)

    def show_search_results(self, collection, media_list):
        if media_list:
            num_media = media_list['totalCount']
            if num_media == 0:
                InfoDialog(get_string(30302)).notify()
                self.router.replace_route(ROUTE.SEARCH, collection)
            else:
                self.render_media_list(media_list, collection)
                if not self.media_list_renderer.is_same_list():
                    InfoDialog(get_string(30303).format(number=str(num_media))).notify()

    def render_media_list(self, media_list, as_type):
        self.media_list_renderer(media_list, as_type)

    def filter_media(self, collection, filter_name, search_value):
        api_response = self._api.media_filter(collection, filter_name, search_value)
        return self.get_media(api_response)

    def get_media(self, api_call):
        response = self.api_response_handler(api_call)
        if response is None:
            return
        json = response.json()
        return json

    @staticmethod
    def api_response_handler(response):
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            InfoDialog(get_string(30301), icon=InfoDialogType.ERROR).notify()
            logger.error(e)
            return None

    def _check_provider(self):
        if self._provider.username == '' or self._provider.username == '':
            InfoDialog(get_string(30300), sound=True).notify()
            return False
        return True

    def _check_token(self):
        if self._provider.token == '':
            if not self._check_provider():
                settings.show()
            else:
                settings[SETTINGS.PROVIDER_TOKEN] = self._provider.get_token()
            return False
        return True

    def play_stream(self, ident):
        logger.debug('Trying to play stream')
        if self._check_token():
            logger.debug('Provider token is valid')
            stream_url = self._provider.get_link_for_file_with_id(ident)
            logger.debug('Stream URL found. Playing %s' % stream_url)
            self.router.set_resolved_url(stream_url)

    def SIGNIN(self):
        dialog = xbmcgui.Dialog()
        # if dialog.yesno("%s"%(addon_name), 'Do you Wish To Sign In','', "",'Dont Have An Account','Sign In'):
        #     email=Search('username')
        #     ADDON.setSetting('username',email)
        #     password=Search('Password')
        #     ADDON.setSetting('password',password)
        #     logincheck=urllib.urlopen('%s/logincheck.php?username=%s&password=%s'%(BASE,email,password)).read()
        #     if logincheck == "wrong":
        #         dialog.ok("Error", "Wrong Username And Password")
        #         return
        #     if logincheck == "correct":
        #         fullname=urllib.urlopen('%s/username.php?username=%s'%(BASE,email)).read()
        #         dialog.ok("Login Successful !", " Thank You For Login In %s Enjoy The VIP Channels"%(fullname))
        #         ADDON.setSetting('login','true')
        #         xbmc.executebuiltin('Container.Refresh')
        # else:
        #     dialog.ok("Get An Account", "Head Over To http://mykodi.co.uk And Sign Up ")
        #     return
