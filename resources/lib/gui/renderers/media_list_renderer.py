import xbmcplugin

from resources.lib.const import CACHE, ROUTE, STORAGE
from resources.lib.gui import MainMenuFolderItem, DirectoryItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_string, set_resolved_url, router_url_from_string
from resources.lib.utils.url import Url


class MediaListRenderer(Renderer):
    def __init__(self, router, on_stream_selected):
        """

        :param callable on_stream_selected: Called when a stream is selected.
        """
        super(MediaListRenderer, self).__init__(router)
        self._previous_media_list = self.get_cached_media()
        self._on_stream_selected = on_stream_selected

    def __call__(self, collection, media_list):
        logger.debug('Renderer %s call' % self)
        self.set_cache(STORAGE.COLLECTION, collection)
        self.set_cache(STORAGE.MEDIA_LIST, media_list)

    def __repr__(self):
        return self.__class__.__name__

    def is_same_list(self):
        prev = self._previous_media_list.get('url')
        curr = self.get_cached_media().get('url')
        if prev and curr:
            return Url.remove_params(prev) == Url.remove_params(curr)
        return False

    @property
    def media_list_pages(self):
        return self.build_page_object(self.storage)

    @property
    def last_media_list_pages(self):
        return self.build_page_object(self._previous_media_list)

    @property
    def storage(self):
        return storage

    @staticmethod
    def build_page_object(media_list):
        return {
            'prev': media_list.get('prev'),
            'next': media_list.get('next')
        }

    def render(self, list_items):
        # as_type=None causes all items to show their icons
        with DirectoryRenderer.start_directory(self.handle, as_type=self.get_collection()):
            xbmcplugin.addDirectoryItems(self.handle, list_items)

    @staticmethod
    def add_navigation(list_items, bottom=False):
        list_items.insert(0, MainMenuFolderItem(url=router_url_from_string(ROUTE.MAIN_MENU)))
        if bottom:
            list_items.append(MainMenuFolderItem(url=router_url_from_string(ROUTE.MAIN_MENU)))

    def add_paging(self, list_items, paging):
        next_page = None if paging is None else 'next' in paging
        if next_page:
            list_items.insert(0, self.next_page_item(paging))
            list_items.append(self.next_page_item(paging))

    def next_page_item(self, media_list):
        return DirectoryItem(
            title=self.next_page_title(media_list['page'], media_list['pageCount']),
            url=router_url_from_string(ROUTE.NEXT_PAGE, self.get_collection(), Url.quote_plus(media_list['next'])))

    @staticmethod
    def next_page_title(page, page_count):
        return '{} ({}/{})'.format(get_string(30203), page, page_count)

    def select_stream(self, media_id, streams):
        self.storage[STORAGE.SELECTED_MEDIA_ID] = media_id
        stream = DialogRenderer.choose_video_stream(streams)
        if stream is None:
            # Dialog cancel.
            set_resolved_url(self.handle)
            return

        logger.info('Got movie stream')
        self._on_stream_selected(stream['ident'])

    def get_cached_media(self):
        media = self.storage.get(STORAGE.MEDIA_LIST)
        return {} if media is None else media

    def get_collection(self):
        return self.storage.get(STORAGE.COLLECTION)

    def set_cache(self, key, value):
        self.storage[key] = value

    def get_cached_media_by_id(self, media_id):
        for media in self.get_cached_media()['data']:
            if media['_id'] == media_id:
                return media

    def build_media_list_gui(self, item_type, media_list_data, url_builder, *args):
        return [self.build_media_item_gui(item_type, media, url_builder, *args) for media in media_list_data]

    @staticmethod
    def build_media_item_gui(item_type, media, url_builder, *args):
        info_labels = media.get('info_labels')
        info_labels.update({'imdbnumber': media.get('services').get('imdb')})

        return item_type(
            title=info_labels.get('title'),
            url=url_builder(media, *args),
            art=media.get('art'),
            info_labels=info_labels,
            stream_info=MediaListRenderer.stream_info(media),
        )

    @staticmethod
    def stream_info(media):
        streams = media.get('streams', [])
        if len(streams) == 0:
            return
        stream = streams.pop()
        stream_info = {
            'video': {
                'codec': stream.get('codec'),
                'aspect': stream.get('aspect'),
                'width': stream.get('width'),
                'height': stream.get('height'),
                'duration': stream.get('duration'),
            },
        }
        audios = stream.get('audio')
        if len(audios) > 0:
            stream_info.update({
                'audio': audios[0]
            })
        subtitles = stream.get('subtitles')
        if len(subtitles) > 0:
            stream_info.update({
                'subtitle': subtitles[0]
            })
        logger.debug('Generated stream info')
        return stream_info
