import xbmcplugin

from resources.lib.const import ROUTE, STORAGE, explicit_genres, api_genres
from resources.lib.gui import MainMenuFolderItem, DirectoryItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_string, set_resolved_url, router_url_from_string
from resources.lib.utils.url import Url


class MediaListRenderer(Renderer):
    def __init__(self, router, on_stream_selected, _on_media_selected):
        """

        :param callable on_stream_selected: Called when a stream is selected.
        """
        super(MediaListRenderer, self).__init__(router)
        self._on_stream_selected = on_stream_selected
        self._on_media_selected = _on_media_selected

    def __call__(self, collection, media_list):
        logger.debug('Renderer %s call' % self)
        storage[STORAGE.COLLECTION] = collection

    def __repr__(self):
        return self.__class__.__name__

    @staticmethod
    def is_same_list(router):
        prev = router.history.previous()
        curr = router.history.current()
        if prev and curr:
            return Url.remove_params(prev) == Url.remove_params(curr)
        return False

    @property
    def storage(self):
        return storage

    @staticmethod
    def build_page_object(media_list):
        return {
            'prev': media_list.get('prev'),
            'next': media_list.get('next')
        }

    def render(self, collection, list_items):
        # as_type=None causes all items to show their icons
        with DirectoryRenderer.start_directory(self.handle, as_type=collection):
            xbmcplugin.addDirectoryItems(self.handle, list_items)

    @staticmethod
    def add_navigation(list_items, bottom=False):
        list_items.insert(0, MainMenuFolderItem(url=router_url_from_string(ROUTE.CLEAR_PATH)))
        if bottom:
            list_items.append(MainMenuFolderItem(url=router_url_from_string(ROUTE.CLEAR_PATH)))

    @staticmethod
    def add_paging(collection, list_items, paging):
        next_page = None if paging is None else 'next' in paging
        if next_page:
            list_items.insert(0, MediaListRenderer.next_page_item(collection, paging))
            list_items.append(MediaListRenderer.next_page_item(collection, paging))

    @staticmethod
    def next_page_item(collection, media_list):
        return DirectoryItem(
            title=MediaListRenderer.next_page_title(media_list['page'], media_list['pageCount']),
            url=router_url_from_string(ROUTE.NEXT_PAGE, collection, Url.quote_plus(media_list['next'])))

    @staticmethod
    def next_page_title(page, page_count):
        return '{} ({}/{})'.format(get_string(30203), page, page_count)

    def select_stream(self, media_id, streams):
        stream = DialogRenderer.choose_video_stream(streams)
        if stream is None:
            # Dialog cancel.
            # set_resolved_url(self.handle)
            return False

        logger.info('Got movie stream')
        self.storage[STORAGE.SELECTED_MEDIA_ID] = media_id
        self._on_stream_selected(stream['ident'])

    def get_cached_media(self):
        return self.storage.get(STORAGE.MEDIA_LIST)

    def set_cached_media(self, value):
        self.storage[STORAGE.MEDIA_LIST] = value

    @staticmethod
    def build_media_item_gui(item_type, media, url, title=None):
        info_labels = media.get('info_labels')
        info_labels.update({'imdbnumber': str(media.get('services').get('imdb'))})
        del info_labels['playcount']
        return item_type(
            title=title if title else info_labels.get('title'),
            url=url,
            art=media.get('art'),
            info_labels=info_labels,
            stream_info=MediaListRenderer.stream_info(media),
            services=media.get('services')
        )

    @staticmethod
    def explicit_filter(media_list):
        filtered_list = []
        explicit_genres_str = [api_genres[i] for i in explicit_genres]
        for media in media_list.get('data'):
            genres = media.get('info_labels').get('genre')
            is_blocked = bool(set(genres).intersection(explicit_genres_str))
            if is_blocked:
                continue
            filtered_list.append(media)
        media_list.update({'data': filtered_list})

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
