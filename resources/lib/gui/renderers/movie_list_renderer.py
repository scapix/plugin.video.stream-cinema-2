from resources.lib.gui import MediaItem
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer


class MovieListRenderer(MediaListRenderer):
    def __call__(self, collection, media_list):
        super(MovieListRenderer, self).__call__(collection, media_list)
        gui_items = self.build_media_list_gui(MediaItem, media_list.get('data'), self.url_builder)
        paging = media_list.get('paging')
        is_paging = True if paging else False
        self.add_paging(gui_items, paging)
        self.add_navigation(gui_items, bottom=is_paging)
        built_items = [media.build() for media in gui_items]
        self.render(built_items)

    def select_movie_stream(self, media_id):
        media = self.get_cached_media_by_id(media_id)
        super(MovieListRenderer, self).select_stream(media_id, media['streams'])

    def url_builder(self, media):
        return self._router.url_for(self.select_movie_stream, media.get('_id'))
