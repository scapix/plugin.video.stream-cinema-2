import xbmc
import xbmcplugin

from resources.lib.cache import Cache
from resources.lib.const import CACHE, ROUTE
from resources.lib.gui import FolderBackItem, DirectoryItem, MediaItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog import DialogRenderer
from resources.lib.gui.renderers.directory import DirectoryRenderer
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import get_string, router_url_for, set_resolved_url, go_to_plugin_url
from resources.lib.utils.url import Url


class MediaListRenderer(Renderer):
    _storage_id = CACHE.MEDIA_LIST_RENDERER

    def __init__(self, router):
        super(MediaListRenderer, self).__init__(router)
        self._storage = Cache(self._storage_id)
        self._previous_media_list = self.get_cached_media()

    def __call__(self, media_list, collection, *args, **kwargs):
        self._collection = collection
        self.set_cached_media(media_list)
        logger.debug('SAME LIST %s' % self.is_same_list())
        self._render(self.handle, media_list)

    def render(self):
        self._render(self.handle, self.get_cached_media())

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
        return self._storage

    @staticmethod
    def build_page_object(media_list):
        return {
            'prev': media_list.get('prev'),
            'next': media_list.get('next')
        }

    def _render(self, handle, media_list):
        with DirectoryRenderer.start_directory(handle, as_type=self._collection):
            xbmcplugin.addDirectoryItems(
                handle,
                [movie.build() for movie in self.build_media_list_gui(self._collection, media_list)]
            )

    def build_media_list_gui(self, collection, media_list):
        gui_media_list = []
        next_page = 'next' in media_list
        if next_page:
            gui_media_list.append(self.next_page_item(collection, media_list['next']))
            gui_media_list.append(FolderBackItem(url='/main_menu'))
        for media in media_list['data']:
            info_labels = {}
            # Info labels supported by the backend.
            LABELS = [
                'genre', 'year', 'episode', 'season', 'top250', 'tracknumber',
                'rating', 'watched', 'playcount', 'overlay',
                'castandrole', 'director', 'mpaa', 'plot', 'plotoutline',
                'title', 'originaltitle', 'sorttitle', 'duration', 'studio',
                'tagline', 'writer', 'tvshowtitle', 'premiered', 'status',
                'aired', 'credits', 'lastplayed', 'album', 'artist', 'votes',
                'trailer', 'dateadded', 'count', 'date', 'imdbnumber',
                'mediatype'
            ]
            for label in LABELS:
                if label in media:
                    info_labels[label] = media[label]
            # Deserialize cast. It must be a list.
            cast = media.get('cast', '').split(',')
            info_labels['cast'] = cast

            # Extract the ID of the movie that is used in SC.
            url = self._router.url_for(self.select_stream, media.get('_id'))

            # Provide some metadata that are shown as the badges in the corner of the screen.
            stream_info = {
                'video': media.get('mvideo', {}),
                'audio': media.get('maudio', {}),
                'subtitle': media.get('msubtitle', {}),
            }

            gui_video = MediaItem(
                title=media['title'],
                url=url,
                art=media.get('art'),
                info_labels=info_labels,
                stream_info=stream_info,
            )
            gui_media_list.append(gui_video)

        if next_page:
            gui_media_list.append(self.next_page_item(collection, media_list['next']))
        return gui_media_list

    def next_page_item(self, collection, url):
        return DirectoryItem(
            title=get_string(30203),
            url=router_url_for(ROUTE.NEXT_PAGE, collection, Url.quote_plus(url)))

    def select_stream(self, media_id):
        video = self.get_cached_media_by_id(media_id)
        stream = DialogRenderer.choose_video_stream(video['streams'])
        if stream is None:
            # Dialog cancel.
            set_resolved_url(self.handle)
            return

        logger.info('Got movie stream')
        self._router.go_to_route(ROUTE.PLAY_STREAM, stream['ident'])

    def get_cached_media(self):
        media = self.storage.get('media')
        return {} if media is None else media

    def set_cached_media(self, value):
        self.storage['media'] = value

    def get_cached_media_by_id(self, media_id):
        for media in self.get_cached_media()['data']:
            if media['_id'] == media_id:
                return media
