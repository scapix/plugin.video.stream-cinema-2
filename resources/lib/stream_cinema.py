"""
    Main GUI.
"""

import requests
import xbmcgui

from resources.lib.const import SETTINGS, FILTER_TYPE, ROUTE, RENDERER, explicit_genres, STORAGE, SERVICE, \
    SERVICE_EVENT, COLLECTION, LANG
from resources.lib.gui import InfoDialog, InfoDialogType
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.movie_list_renderer import MovieListRenderer
from resources.lib.gui.renderers.tv_show_list_renderer import TvShowListRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_string
from resources.lib.utils.url import Url


class StreamCinema:
    def __init__(self, provider, api, router=None):
        self._api = api
        self._router = router
        self._provider = provider

        directory_renderer = DirectoryRenderer(router)
        movie_renderer = MovieListRenderer(router, on_stream_selected=self.play_stream)
        tv_show_renderer = TvShowListRenderer(router, on_stream_selected=self.play_stream)
        self.renderers = {
            RENDERER.MOVIES: movie_renderer,
            RENDERER.TV_SHOWS: tv_show_renderer,
            RENDERER.DIRECTORIES: directory_renderer
        }

        router.add_route(movie_renderer.select_movie_stream, ROUTE.SELECT_STREAM)
        router.add_route(tv_show_renderer.select_season, ROUTE.SELECT_SEASON)
        router.add_route(tv_show_renderer.select_episode, ROUTE.SELECT_EPISODE)
        router.add_route(tv_show_renderer.select_tv_show_stream, ROUTE.SELECT_TV_SHOW_STREAM)
        router.add_route(directory_renderer.search, ROUTE.SEARCH)
        router.add_route(directory_renderer.main_menu, ROUTE.MAIN_MENU)
        router.add_route(directory_renderer.media_menu, ROUTE.MEDIA_MENU)
        router.add_route(directory_renderer.command, ROUTE.COMMAND)
        router.add_route(directory_renderer.a_to_z_menu, ROUTE.A_TO_Z)
        router.add_route(directory_renderer.genre_menu, ROUTE.GENRE_MENU)
        router.add_route(self.next_page, ROUTE.NEXT_PAGE)
        router.add_route(self.search_result, ROUTE.SEARCH_RESULT)
        router.add_route(self.filter, ROUTE.FILTER)
        router.add_route(self.popular_media, ROUTE.POPULAR)


    @property
    def router(self):
        return self._router

    def _filter_and_render(self, collection, filter_type, filter_value):
        media = self.filter_media(collection, filter_type, filter_value)
        self.show_search_results(collection, media)

    def next_page(self, collection, url):
        url = Url.unquote_plus(url)
        media = self.get_media(self._api.next_page(url))
        self.render_media_list(collection, media)

    def filter(self, collection, filter_type, filter_value):
        self._filter_and_render(collection, filter_type, filter_value)

    def search_result(self, collection, search_value):
        self.filter(collection, FILTER_TYPE.TITLE_OR_ACTOR, search_value)

    def show_search_results(self, collection, media_list):
        if media_list:
            num_media = media_list.get('totalCount')
            if num_media == 0:
                InfoDialog(get_string(30302)).notify()
                # if collection == COLLECTION.TV_SHOWS:
                #     self.router.back(steps=1, skip_search=True)
            else:
                if not settings.as_bool(SETTINGS.EXPLICIT_CONTENT):
                    self.vulgar_filter(media_list)
                self.render_media_list(collection, media_list)
                if not self.renderers[collection].is_same_list():
                    InfoDialog(get_string(30303).format(number=str(num_media))).notify()

    @staticmethod
    def vulgar_filter(media_list):
        filtered_list = []
        explicit_genres_str = [get_string(i) for i in explicit_genres]
        for media in media_list.get('data'):
            genres = media.get('info_labels').get('genre')
            is_blocked = bool(set(genres).intersection(explicit_genres_str))
            if is_blocked:
                continue
            filtered_list.append(media)
        media_list.update({'data': filtered_list})

    def render_media_list(self, collection, media_list):
        self.renderers[collection](collection, media_list)

    def popular_media(self, collection):
        api_response = self._api.popular_media(collection)
        self.show_search_results(collection, self.get_media(api_response))

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
            InfoDialog(get_string(LANG.MISSING_PROVIDER_CREDENTIALS), sound=True).notify()
            settings.show()
            return False
        return True

    def _check_token(self):
        if self._provider.token == '':
            if self._check_provider():
                settings[SETTINGS.PROVIDER_TOKEN] = self._provider.get_token()
            return False
        return True

    def _check_vip(self):
        if not self._provider.is_vip():
            InfoDialog(get_string(LANG.ACTIVATE_VIP), sound=True).notify()
            return False
        return True

    def _check_account(self):
        if self._check_provider():
            return self._check_token() and self._check_vip()
        return False

    def play_stream(self, ident):
        logger.debug('Trying to play stream')
        if self._check_account():
            logger.debug('Provider token is valid')
            stream_url = self._provider.get_link_for_file_with_id(ident)
            logger.debug('Stream URL found. Playing %s' % stream_url)
            self.send_service_message(SERVICE.PLAYER_SERVICE, SERVICE_EVENT.PLAYBACK_STARTED)
            self.router.set_resolved_url(stream_url)

    @staticmethod
    def send_service_message(service_name, service_event):
        logger.debug('Sending service message {}: {}'.format(service_name, service_event))
        service_storage = storage.get(STORAGE.SERVICE)
        service_storage[service_name] = service_event
        storage[STORAGE.SERVICE] = service_storage

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
