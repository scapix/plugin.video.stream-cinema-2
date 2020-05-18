"""
    Main GUI.
"""
import json
from datetime import datetime

import requests
import xbmcplugin

from resources.lib.api.api import API
from resources.lib.const import SETTINGS, FILTER_TYPE, ROUTE, RENDERER, STORAGE, SERVICE_EVENT, LANG, \
    SERVICE, MEDIA_TYPE, COLLECTION, STRINGS, GENERAL, ORDER, SORT_TYPE
from resources.lib.gui import InfoDialog, InfoDialogType, MediaItem, TvShowMenuItem
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.gui.renderers.movie_list_renderer import MovieListRenderer
from resources.lib.gui.renderers.tv_show_list_renderer import TvShowListRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_string, time_limit_expired, translate_genres
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
        router.add_route(movie_renderer.csfd_tips, ROUTE.CSFD_TIPS)
        router.add_route(self.search_for_csfd_item, ROUTE.SEARCH_CSFD_ITEM)
        router.add_route(self.sort, ROUTE.SORT)

    @property
    def router(self):
        return self._router

    def clear_path(self):
        logger.debug('Clearing path')
        self.router.replace_route(ROUTE.ROOT)

    def _filter_and_render(self, collection, filter_type, filter_value, order):
        media = self.filter_media(collection, filter_type, filter_value, order)
        self.show_search_results(media, self.show_mixed_media_list)

    def next_page(self, collection, url, body):
        url = Url.unquote_plus(url)
        body = json.loads(Url.decode_param(body))
        media = self.process_api_response(self._api.post(url, body))
        self.render_media_list(media, collection)

    def filter(self, collection, filter_type, filter_value, order):
        self._filter_and_render(collection, filter_type, filter_value, order)

    def search_result(self, collection, search_value):
        self.filter(collection, FILTER_TYPE.FUZZY_SEARCH,
                    Url.unquote_plus(search_value).encode('utf-8'), ORDER.DESCENDING)

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
                if not MediaListRenderer.is_same_list(self.router) and settings.as_bool(SETTINGS.SHOW_RESULTS_COUNT):
                    InfoDialog(get_string(30303).format(number=str(num_media))).notify()
                return callback(media_list, *args)

    def render_media_list(self, media_list, collection):
        self.renderers[collection](collection, media_list)

    def popular_media(self, collection):
        api_response = self._api.popular_media(collection)
        self.show_search_results(self.process_api_response(api_response), self.render_media_list, collection)

    def filter_media(self, collection, filter_name, search_value, order):
        api_response = self._api.media_filter(collection, filter_name, Url.decode_param(search_value), order)
        return self.process_api_response(api_response)

    def process_api_response(self, api_call):
        response = self.api_response_handler(api_call)
        if response is None:
            return
        return response.json()

    def search_for_csfd_item(self, collection, search_value):
        # No idea how to decode search_value to correct format. It must be decoded on the server right now.
        media_list = self.filter_media(collection, FILTER_TYPE.EXACT_TITLE, Url.encode_param([search_value]), ORDER.ASCENDING).get('data')
        num_media = len(media_list)
        if num_media == 1:
            media_id = media_list.pop().get('_id')
            streams = API.get_source(self.get_media_detail(collection, media_id)).get('streams')
            self.renderers[RENDERER.MOVIES].select_stream(media_id, streams)
        elif num_media == 0:
            InfoDialog(get_string(30303).format(number=str(num_media))).notify()

    @staticmethod
    def api_response_handler(response):
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            InfoDialog(get_string(30301), icon=InfoDialogType.ERROR).notify()
            logger.error(e)
            return None

    def _check_provider_settings(self):
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
            settings.set_cache(SETTINGS.PROVIDER_TOKEN, token)
            return True
        InfoDialog(get_string(LANG.INCORRECT_PROVIDER_CREDENTIALS), sound=True).notify()
        return False

    def _check_vip(self, user_data):
        logger.debug('Checking VIP')
        is_vip = self._provider.is_vip(user_data)
        if not is_vip:
            logger.debug('VIP is not active')
            InfoDialog(get_string(LANG.ACTIVATE_VIP), sound=True).notify()
            vip_string = get_string(LANG.NOT_ACTIVE)
        else:
            logger.debug('VIP is active')
            vip_string = STRINGS.VIP_INFO.format(self._provider.vip_until(user_data),
                                                 get_string(LANG.DAYS),
                                                 self._provider.vip_remains(user_data))
        settings[SETTINGS.VIP_DURATION] = vip_string
        return is_vip

    def vip_remains(self):
        if time_limit_expired(SETTINGS.LAST_VIP_CHECK, GENERAL.VIP_CHECK_INTERVAL):
            settings[SETTINGS.LAST_VIP_CHECK] = datetime.now()
            valid_token, user_data = self._check_token_and_return_user_data()
            if valid_token:
                if self._check_vip(user_data):
                    days_to = self._provider.vip_remains(user_data)
                    if days_to <= GENERAL.VIP_REMAINING_DAYS_WARN:
                        DialogRenderer.ok(get_string(LANG.VIP_REMAINS).format(provider=self._provider),
                                          STRINGS.PAIR_BOLD.format(get_string(LANG.DAYS), str(days_to)))

    def _check_token_and_return_user_data(self):
        logger.debug('Checking token and returning user data.')
        if self._check_provider_settings():
            user_data = self._provider.get_user_data()
            if not self._provider.is_valid_token(user_data):
                logger.debug('Token is not valid. Getting new one and then new user data.')
                return self.ensure_provider_token(), self._provider.get_user_data()
            logger.debug('Token is valid.')
            return True, user_data
        return False, None

    def _check_account(self):
        logger.debug('Checking account.')
        valid_token, user_data = self._check_token_and_return_user_data()
        if valid_token:
            logger.debug('Provider token is valid')
            return self._check_vip(user_data)
        return False

    def play_stream(self, ident):
        logger.debug('Trying to play stream.')
        if self._check_account():

            stream_url = self._provider.get_link_for_file_with_id(ident)
            logger.debug('Stream URL found. Playing %s' % stream_url)
            self.send_service_message(SERVICE.PLAYER_SERVICE, SERVICE_EVENT.PLAYBACK_STARTED)
            self.router.set_resolved_url(stream_url)
        else:
            self.router.set_resolved_url()

    def get_media_detail(self, collection, media_id):
        storage[STORAGE.SELECTED_MEDIA_ID] = media_id
        storage[STORAGE.COLLECTION] = collection
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

    def sort(self, collection, sort_type, order):
        media_list = self.process_api_response(self._api.sort(collection, sort_type, order))
        self.show_search_results(media_list, self.show_mixed_media_list)

    def show_mixed_media_list(self, media_list):
        media_list_gui = []
        for media in media_list.get('data'):
            source = API.get_source(media)
            media_type = source.get('info_labels').get('mediatype')
            info_labels = source.get('info_labels')
            genres = translate_genres(info_labels.get('genre'))
            title = STRINGS.TITLE_GENRE_YEAR.format(title=info_labels.get('title').encode('utf-8'), genre=' / '.join(genres), year=info_labels.get('year'))
            if media_type == MEDIA_TYPE.TV_SHOW:
                media_list_gui.append(MediaListRenderer.build_media_item_gui(TvShowMenuItem, source, self.renderers[
                    RENDERER.TV_SHOWS].url_builder(media, COLLECTION.TV_SHOWS), title=title).build())
            elif media_type == MEDIA_TYPE.MOVIE:
                media_list_gui.append(MovieListRenderer.build_media_item_gui(MediaItem, source, self.renderers[
                    RENDERER.MOVIES].url_builder(media, COLLECTION.MOVIES), title=title).build())
        with DirectoryRenderer.start_directory(self.router.handle, as_type=COLLECTION.MOVIES):
            xbmcplugin.addDirectoryItems(self.router.handle, media_list_gui)
