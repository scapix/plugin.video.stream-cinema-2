from resources.lib.api.api import API
from resources.lib.const import ROUTE, STRINGS
from resources.lib.gui import MediaItem
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import logger
from resources.lib.utils.csfd_tips import get_csfd_tips
from resources.lib.utils.kodiutils import router_url_from_string
from resources.lib.utils.url import Url


class MovieListRenderer(MediaListRenderer):
    def __call__(self, collection, media_list):
        super(MovieListRenderer, self).__call__(collection, media_list)
        gui_items = [self.build_media_item_gui(MediaItem, media,
                                               self.url_builder(media, collection)) for media in media_list.get('data')]
        pagination = media_list.get('pagination')
        is_pagination = True if pagination else False
        self.add_pagination(collection, gui_items, pagination)
        self.add_navigation(gui_items, bottom=is_pagination)
        built_items = [media.build() for media in gui_items]
        self.render(collection, built_items)

    def select_movie_stream(self, collection, media_id):
        media = self._on_media_selected(collection, media_id)
        super(MovieListRenderer, self).select_stream(media_id, API.get_source(media)['streams'])

    def url_builder(self, media, collection):
        return self._router.url_for(self.select_movie_stream, collection, media.get('_id'))

    def csfd_tips(self, collection):
        logger.debug('CSFD tips search opened')
        with DirectoryRenderer.start_directory(self.handle, as_type=collection):
            for tip in get_csfd_tips():
                name = tip[0][:-7]
                name_quoted = tip[0][:-7].replace(' ', '%20')
                year = tip[0][-7:]
                year = year[2:-1]
                tip_joined = STRINGS.TITLE_GENRE_YEAR.format(title=name, genre=tip[1], year=year)
                info_labels = {
                    'title': name,
                    'year': int(year)
                }
                MediaItem(title=tip_joined,
                          url=router_url_from_string(ROUTE.SEARCH_CSFD_ITEM, collection, Url.quote(name_quoted)),
                          info_labels=info_labels)(self.handle)
