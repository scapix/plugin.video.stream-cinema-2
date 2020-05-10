from resources.lib.const import STRINGS
from resources.lib.gui import DirectoryItem, TvShowItem, MediaItem
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import get_string


class TvShowListRenderer(MediaListRenderer):
    def __call__(self, collection, media_list):
        super(TvShowListRenderer, self).__call__(collection, media_list)
        gui_items = self.build_media_list_gui(TvShowItem, media_list.get('data'), self.url_builder)
        paging = media_list.get('paging')
        is_paging = True if paging else False
        self.add_paging(gui_items, paging)
        self.add_navigation(gui_items, bottom=is_paging)
        built_items = [media.build() for media in gui_items]
        self.render(built_items)

    def url_builder(self, media):
        return self._router.url_for(self.select_season, media.get('_id'))

    def stream_url_builder(self, media, media_id, season_id, episode_id):
        return self._router.url_for(self.select_tv_show_stream, media_id, season_id, episode_id)

    def select_season(self, media_id):
        logger.debug('Showing season list')
        media = self._on_media_selected(self.get_collection(), media_id)
        self.set_cached_media(media)
        season_list = media.get('seasons')
        if season_list:
            list_items = [movie.build() for movie in self.build_season_list_gui(media_id, season_list)]
            self.render(list_items)

    def build_season_list_gui(self, media_id, season_list):
        gui_season_list = []
        for season_id, season in enumerate(season_list, start=1):
            title = STRINGS.SEASON_TITLE.format(get_string(30920), str(season_id))
            url = self._router.url_for(self.select_episode, media_id, season_id - 1)
            item = DirectoryItem(title, url)
            gui_season_list.append(item)
        return gui_season_list

    def build_episode_list_gui(self, media_id, episode_list, season_id):
        gui_list = []
        for episode_id, episode in enumerate(episode_list):
            gui_list.append(self.build_media_item_gui(MediaItem, episode, self.stream_url_builder, media_id, season_id, episode_id))
        return gui_list

    def select_episode(self, media_id, season_id):
        logger.debug('Showing episode list')
        episode_list = self.get_season(int(season_id)).get('episodes')
        if episode_list:
            list_items = [movie.build() for movie in self.build_episode_list_gui(media_id, episode_list, season_id)]
            self.render(list_items)

    def select_tv_show_stream(self, media_id, season_id, episode_id):
        logger.debug('Showing stream list')
        media = self.get_episode(int(season_id), int(episode_id))
        self.select_stream(media_id, media['streams'])

    def get_season(self, season_id):
        return self.get_cached_media().get('seasons')[season_id]

    def get_episode(self, season_id, episode_id):
        return self.get_season(season_id).get('episodes')[episode_id]
