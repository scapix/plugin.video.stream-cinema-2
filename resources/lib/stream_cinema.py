"""
    Main GUI.
"""

import requests
import xbmcgui
import xbmcplugin

from resources.lib.const import SETTINGS, FILTER_TYPE, ROUTE, RENDERER, explicit_genres, STORAGE, SERVICE_EVENT, LANG, \
    SERVICE, MEDIA_TYPE, COLLECTION
from resources.lib.gui import InfoDialog, InfoDialogType, MediaItem, TvShowItem
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.gui.renderers.movie_list_renderer import MovieListRenderer
from resources.lib.gui.renderers.tv_show_list_renderer import TvShowListRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.storage.storage import Storage, storage
from resources.lib.utils.kodiutils import get_string, router_url_from_string, replace_plugin_url
from resources.lib.utils.url import Url


class StreamCinema:
    def __init__(self, provider, api, router=None):
        self._api = api
        self._router = router
        self._provider = provider

        directory_renderer = DirectoryRenderer(router, on_a_to_z_menu=self.get_filter_values_count)
        movie_renderer = MovieListRenderer(router, on_stream_selected=self.play_stream,
                                           _on_media_selected=self.get_media_detail)
        tv_show_renderer = TvShowListRenderer(router, on_stream_selected=self.play_stream,
                                              _on_media_selected=self.get_media_detail)
        self.renderers = {
            RENDERER.MOVIES: movie_renderer,
            RENDERER.TV_SHOWS: tv_show_renderer,
            RENDERER.DIRECTORIES: directory_renderer
        }

        router.add_route(self.clear_path, ROUTE.CLEAR_PATH)
        router.add_route(tv_show_renderer.select_season, ROUTE.SELECT_SEASON)
        router.add_route(tv_show_renderer.select_episode, ROUTE.SELECT_EPISODE)
        router.add_route(tv_show_renderer.select_tv_show_stream, ROUTE.SELECT_TV_SHOW_STREAM)
        router.add_route(directory_renderer.search, ROUTE.SEARCH)
        router.add_route(directory_renderer.main_menu, ROUTE.MAIN_MENU)
        router.add_route(directory_renderer.media_menu, ROUTE.MEDIA_MENU)
        router.add_route(directory_renderer.command, ROUTE.COMMAND)
        router.add_route(movie_renderer.select_movie_stream, ROUTE.SELECT_MOVIE_STREAM)
        router.add_route(directory_renderer.a_to_z_menu, ROUTE.A_TO_Z)
        router.add_route(directory_renderer.a_to_z_submenu, ROUTE.A_TO_Z_SUBMENU)
        router.add_route(directory_renderer.genre_menu, ROUTE.GENRE_MENU)
        router.add_route(self.next_page, ROUTE.NEXT_PAGE)
        router.add_route(self.search_result, ROUTE.SEARCH_RESULT)
        router.add_route(self.filter, ROUTE.FILTER)
        router.add_route(self.popular_media, ROUTE.POPULAR)
        router.add_route(self.watched, ROUTE.WATCHED)

    @property
    def router(self):
        return self._router

    def clear_path(self):
        logger.debug('Clearing path')
        self.router.replace_route(ROUTE.ROOT)

    def _filter_and_render(self, collection, filter_type, filter_value):
        media = self.filter_media(collection, filter_type, filter_value)
        self.show_search_results(media, self.render_media_list, collection)

    def next_page(self, collection, url):
        url = Url.unquote_plus(url)
        media = self.process_api_response(self._api.next_page(url))
        self.render_media_list(collection, media)

    def filter(self, collection, filter_type, filter_value):
        self._filter_and_render(collection, filter_type, filter_value)

    def search_result(self, collection, search_value):
        self.filter(collection, FILTER_TYPE.TITLE_OR_ACTOR, search_value)

    def show_search_results(self, media_list, callback, *args):
        if media_list:
            num_media = media_list.get('totalCount')
            if num_media == 0:
                InfoDialog(get_string(30302)).notify()
                # if collection == COLLECTION.TV_SHOWS:
                #     self.router.back(steps=1, skip_search=True)
            else:
                if not settings.as_bool(SETTINGS.EXPLICIT_CONTENT):
                    MediaListRenderer.explicit_filter(media_list)
                if not MediaListRenderer.is_same_list(self.router):
                    InfoDialog(get_string(30303).format(number=str(num_media))).notify()
                return callback(media_list, *args)

    def render_media_list(self, media_list, collection):
        self.renderers[collection](collection, media_list)

    def popular_media(self, collection):
        api_response = self._api.popular_media(collection)
        self.show_search_results(self.process_api_response(api_response), self.render_media_list, collection)

    def filter_media(self, collection, filter_name, search_value):
        api_response = self._api.media_filter(collection, filter_name, search_value)
        return self.process_api_response(api_response)

    def process_api_response(self, api_call):
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
        if self._provider.username == '' or self._provider.password == '':
            InfoDialog(get_string(LANG.MISSING_PROVIDER_CREDENTIALS), sound=True).notify()
            settings.show()
            return False
        return True

    def _check_token(self):
        return self._provider.is_valid_token()

    def ensure_provider_token(self):
        token = self._provider.get_token()
        if token:
            settings[SETTINGS.PROVIDER_TOKEN] = token
            return True
        InfoDialog(get_string(LANG.INCORRECT_PROVIDER_CREDENTIALS), sound=True).notify()
        return False

    def _check_vip(self, user_data):
        if not self._provider.is_vip(user_data):
            InfoDialog(get_string(LANG.ACTIVATE_VIP), sound=True).notify()
            return False
        return True

    def _check_account(self):
        user_data = self._provider.get_user_data()
        if not self._provider.is_valid_token(user_data):
            if self._check_provider():
                if self.ensure_provider_token():
                    logger.debug('Provider token is valid')
                    return self._check_vip(self._provider.get_user_data())
            return False
        return self._check_vip(self._provider.get_user_data())

    def play_stream(self, ident):
        logger.debug('Trying to play stream')
        if self._check_account():

            stream_url = self._provider.get_link_for_file_with_id(ident)
            logger.debug('Stream URL found. Playing %s' % stream_url)
            self.send_service_message(SERVICE.PLAYER_SERVICE, SERVICE_EVENT.PLAYBACK_STARTED)
            self.router.set_resolved_url(stream_url)
        else:
            self.router.set_resolved_url()

    def get_media_detail(self, collection, media_id):
        return self.process_api_response(self._api.media_detail(collection, media_id))

    @staticmethod
    def send_service_message(service_name, service_event):
        logger.debug('Sending service message {}: {}'.format(service_name, service_event))
        service_storage = storage.get(STORAGE.SERVICE)
        service_storage[service_name] = service_event
        storage[STORAGE.SERVICE] = service_storage

    def get_filter_values_count(self, *args, **kwargs):
        return self._api.get_filter_values_count(*args, **kwargs).json()

    def watched(self):
        media_list = self.process_api_response(self._api.watched(settings[SETTINGS.UUID]))
        self.show_search_results(media_list, self.show_mixed_media_list)

    def show_mixed_media_list(self, media_list):
        media_list_gui = []
        for media in media_list.get('data'):
            media_type = media.get('info_labels').get('mediatype')
            if media_type == MEDIA_TYPE.TV_SHOW:
                media_list_gui.append(MediaListRenderer.build_media_item_gui(TvShowItem, media, self.renderers[
                    RENDERER.TV_SHOWS].url_builder, COLLECTION.TV_SHOWS).build())
            elif media_type == MEDIA_TYPE.MOVIE:
                media_list_gui.append(MovieListRenderer.build_media_item_gui(MediaItem, media, self.renderers[
                    RENDERER.MOVIES].url_builder, COLLECTION.MOVIES).build())
        with DirectoryRenderer.start_directory(self.router.handle, as_type=COLLECTION.MOVIES):
            xbmcplugin.addDirectoryItems(self.router.handle, media_list_gui)

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
