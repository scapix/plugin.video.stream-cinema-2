import json

import xbmcplugin

from resources.lib.api.api import API
from resources.lib.const import ROUTE, SETTINGS, STORAGE, STREAM_AUTOSELECT, STRINGS, api_genres, explicit_genres
from resources.lib.gui import MainMenuFolderItem, DirectoryItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_string, set_resolved_url, router_url_from_string
from resources.lib.utils.url import Url
from resources.lib import settings


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

    def __repr__(self):
        return self.__class__.__name__

    @staticmethod
    def is_same_list(router):
        prev = router.history.previous()
        return '/next_page' in prev

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
    def add_pagination(collection, list_items, pagination):
        next_page = None if pagination is None else pagination.get('next')
        if next_page:
            list_items.insert(0, MediaListRenderer.next_page_item(collection, pagination))
            list_items.append(MediaListRenderer.next_page_item(collection, pagination))

    @staticmethod
    def next_page_item(collection, pagination):
        body = json.dumps(pagination['body'])
        return DirectoryItem(
            title=MediaListRenderer.next_page_title(pagination['page'], pagination['pageCount']),
            url=router_url_from_string(ROUTE.NEXT_PAGE, collection, Url.quote_plus(pagination['next']), Url.encode_param(body)))

    @staticmethod
    def next_page_title(page, page_count):
        return '{} ({}/{})'.format(get_string(30203), page, page_count)

    def select_stream(self, media_id, streams):
        stream = None

        if len(streams) == 1:
            stream = streams[0]
        elif len(streams) > 1:
            if settings.get_setting_as_bool("auto_select_stream"):
                preferred_quality = int(settings.get_settings(SETTINGS.PREFERRED_QUALITY))
                preferred_language = int(settings.get_settings(SETTINGS.PREFERRED_LANGUAGE))
                stream = self._autoselect_stream(streams, preferred_quality, preferred_language)

        if stream is None:
            stream = DialogRenderer.choose_video_stream(streams)

        if stream is None:
            # Dialog cancel.
            set_resolved_url(self.handle)
            return False

        logger.info('Got movie stream')
        self._on_stream_selected(stream['ident'])

    @staticmethod
    def _autoselect_stream(streams, quality, language):
        """
        Function takes streams to select and indexes of desired quality and language as defined in const.py.

        It enumerates all streams and try to find best match in this order:
        1. find stream with desired language/audio
        2. find stream with desired quality

        If both language and quality is at least in one stream use that (if more streams qualifies, use the first one)

        If not both satisfy the selection
        1. try to find stream with language match (if more streams qualifies, use the first one)
        2. try to find stream with quality match (if more streams qualifies, use the first one)

        If no stream qualifies, use the first avialable stream.

        :param list streams: list of available streams
        :param int quality: desired quality (index in STREAM_AUTOSELECT.QUALITIES)
        :param int language: language desired language (index in STREAM_AUTOSELECT.LANGUAGES)

        returns selected stream
        """
        selected = streams[0]
        reason = 'no-match'
        try:
            with_right_audio = set([])
            with_right_video = set([])
            for i, stream in enumerate(streams):
                for audio in stream['audio']:
                    if audio["language"] == STREAM_AUTOSELECT.LANGUAGES[language]:
                        with_right_audio.add(i)
                        break
                if stream['quality'] == STREAM_AUTOSELECT.QUALITIES[quality]:
                    with_right_video.add(i)
            intersection = with_right_audio.intersection(with_right_video)
            intersection = list(intersection)
            if len(intersection) > 0:
                reason = 'right audio, right quality'
                selected = streams[intersection[0]]
            elif len(with_right_audio) > 0:
                reason = 'right audio'
                selected = streams[list(with_right_audio)[0]]
            elif len(with_right_video) > 0:
                reason = 'right video'
                selected = streams[list(with_right_video)[0]]
        except Exception as e:
            reason = 'error'
            logger.error("autoselect: failed to auto select stream: %s", e)
        logger.debug("autoselect: auto selected stream: %s (reason: %s)", selected, reason)
        return selected


    def get_cached_media(self):
        return self.storage.get(STORAGE.MEDIA_LIST)

    def set_cached_media(self, value):
        self.storage[STORAGE.MEDIA_LIST] = value

    @staticmethod
    def build_media_item_gui(item_type, media, url, title=None):
        source = API.get_source(media)
        info_labels = source.get('info_labels')
        info_labels.update({'imdbnumber': str(source.get('services').get('imdb'))})
        del info_labels['playcount']
        return item_type(
            title=title if title else STRINGS.TITLE_YEAR.format(title=info_labels.get('title').encode('utf-8'), year=info_labels.get('year')),
            url=url,
            art=source.get('art'),
            info_labels=info_labels,
            stream_info=MediaListRenderer.stream_info(source),
            services=source.get('services')
        )

    @staticmethod
    def explicit_filter(media_list):
        filtered_list = []
        explicit_genres_str = [api_genres[i] for i in explicit_genres]
        for media in media_list.get('data'):
            source = API.get_source(media)
            genres = source.get('info_labels').get('genre')
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
