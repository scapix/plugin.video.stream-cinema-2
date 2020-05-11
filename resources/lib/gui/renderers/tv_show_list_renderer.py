from resources.lib.const import STRINGS, ROUTE, LANG
from resources.lib.gui import DirectoryItem, TvShowItem, MediaItem, MainMenuFolderItem, TvShowMenuItem
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import get_string, router_url_from_string


class TvShowListRenderer(MediaListRenderer):
    def __call__(self, collection, media_list):
        super(TvShowListRenderer, self).__call__(collection, media_list)
        gui_items = [self.build_media_item_gui(TvShowMenuItem, media,
                                               self.url_builder(media, collection)) for media in media_list.get('data')]
        paging = media_list.get('paging')
        is_paging = True if paging else False
        self.add_paging(collection, gui_items, paging)
        self.add_navigation(gui_items, bottom=is_paging)
        built_items = [media.build() for media in gui_items]
        self.render(collection, built_items)

    def url_builder(self, media, collection):
        return self._router.url_for(self.select_season, collection, media.get('_id'))

    def stream_url_builder(self, media_id, season_id, episode_id):
        return self._router.url_for(self.select_tv_show_stream, media_id, season_id, episode_id)

    def select_season(self, collection, media_id):
        logger.debug('Showing season list')
        MainMenuFolderItem(url=router_url_from_string(ROUTE.CLEAR_PATH))(self.handle)
        media = self._on_media_selected(collection, media_id)
        self.set_cached_media(media)
        season_list = media.get('seasons')
        if season_list:
            list_items = [movie.build() for movie in self.build_season_list_gui(collection, media_id, season_list)]
            self.render(collection, list_items)

    def build_season_list_gui(self, collection, media_id, season_list):
        gui_season_list = []
        for season_id, season in enumerate(season_list, start=1):
            title = STRINGS.SEASON_TITLE.format(get_string(LANG.SEASON), str(season_id))
            url = self._router.url_for(self.select_episode, collection, media_id, season_id - 1)
            item = DirectoryItem(title, url)
            gui_season_list.append(item)
        return gui_season_list

    def build_episode_list_gui(self, media_id, episode_list, season_id):
        gui_list = []
        for episode_id, episode in enumerate(episode_list):
            title = episode.get('info_labels').get('title')
            title = title if title else STRINGS.EPISODE_TITLE.format(get_string(LANG.EPISODE), str(season_id), str(episode_id))
            gui_list.append(self.build_media_item_gui(TvShowItem, episode,
                                                      self.stream_url_builder(media_id, season_id, episode_id),
                                                      title=title))
        return gui_list

    def select_episode(self, collection, media_id, season_id):
        logger.debug('Showing episode list')
        MainMenuFolderItem(url=router_url_from_string(ROUTE.CLEAR_PATH))(self.handle)
        episode_list = self.get_season(int(season_id)).get('episodes')
        if episode_list:
            list_items = [movie.build() for movie in self.build_episode_list_gui(media_id, episode_list, season_id)]
            self.render(collection, list_items)

    def select_tv_show_stream(self, media_id, season_id, episode_id):
        logger.debug('Showing stream list')
        media = self.get_episode(int(season_id), int(episode_id))
        self.select_stream(media_id, media['streams'])

    def get_season(self, season_id):
        return self.get_cached_media().get('seasons')[season_id]

    def get_episode(self, season_id, episode_id):
        return self.get_season(season_id).get('episodes')[episode_id]
