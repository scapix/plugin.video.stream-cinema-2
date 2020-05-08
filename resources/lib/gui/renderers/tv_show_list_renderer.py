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

    def stream_url_builder(self, media, media_id, season_id, i):
        return self._router.url_for(self.select_tv_show_stream, media_id, season_id, i)

    def select_season(self, media_id):
        logger.debug('Showing season list')
        season_list = self.get_cached_media_by_id(media_id).get('seasons')
        if season_list:
            list_items = [movie.build() for movie in self.build_season_list_gui(season_list, media_id)]
            self.render(list_items)

    def build_season_list_gui(self, season_list, media_id):
        gui_season_list = []
        for i, season in enumerate(season_list, start=1):
            title = STRINGS.SEASON_TITLE.format(get_string(30920), str(i))
            url = self._router.url_for(self.select_episode, media_id, i - 1)
            item = DirectoryItem(title, url)
            gui_season_list.append(item)
        return gui_season_list

    def build_episode_list_gui(self, media_id, episode_list, season_id):
        gui_list = []
        for i, episode in enumerate(episode_list):
            url = self._router.url_for(self.select_tv_show_stream, media_id, season_id, i)
            gui_list.append(self.build_media_item_gui(MediaItem, episode, self.stream_url_builder, media_id, season_id, i))
        return gui_list

    def select_episode(self, media_id, season_id):
        logger.debug('Showing episode list')
        episode_list = self.get_cached_media_by_id(media_id).get('seasons')[int(season_id)].get('episodes')
        if episode_list:
            list_items = [movie.build() for movie in self.build_episode_list_gui(media_id, episode_list, season_id)]
            self.render(list_items)

    def select_tv_show_stream(self, media_id, season_id, episode_id):
        logger.debug('Showing stream list')
        media = self.get_cached_media_by_id(media_id).get('seasons')[int(season_id)].get('episodes')[int(episode_id)]
        self.select_stream(media_id, media['strms'])