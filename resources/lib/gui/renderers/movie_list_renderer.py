from resources.lib.gui import MediaItem
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer


class MovieListRenderer(MediaListRenderer):
    def __call__(self, collection, media_list):
        super(MovieListRenderer, self).__call__(collection, media_list)
        gui_items = self.build_media_list_gui(MediaItem, media_list.get('data'), self.url_builder, collection)
        paging = media_list.get('paging')
        is_paging = True if paging else False
        self.add_paging(collection, gui_items, paging)
        self.add_navigation(gui_items, bottom=is_paging)
        built_items = [media.build() for media in gui_items]
        self.render(collection, built_items)

    def select_movie_stream(self, collection, media_id):
        media = self._on_media_selected(collection, media_id)
        super(MovieListRenderer, self).select_stream(media_id, media['streams'])

    def url_builder(self, media, collection):
        return self._router.url_for(self.select_movie_stream, collection, media.get('_id'))
