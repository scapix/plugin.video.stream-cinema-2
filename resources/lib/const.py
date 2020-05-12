from datetime import timedelta


class URL:
    API = 'https://beta.plugin.sc2.zone/api'
    GITLAB_URL = 'https://git.hotshot.sk/api/v4/'


class GENERAL:
    PLUGIN_ID = 'plugin.video.stream-cinema-2'
    VERSION_CHECK_INTERVAL = timedelta(minutes=2)
    API_TIMEOUT = 10
    VIP_REMAINING_WARN = 700
    VIP_CHECK_INTERVAL = timedelta(days=1)


class FILTER_TYPE:
    TITLE_OR_ACTOR = 'titleOrActor'
    STARTS_WITH_LETTER = 'startsWithL'
    STARTS_WITH = 'startsWith'
    GENRE = 'genre'


class MEDIA_TYPE:
    TV_SHOW = 'tvshow'
    MOVIE = 'movie'


class COLLECTION:
    TV_SHOWS = 'tvshows'
    MOVIES = 'movies'
    DIRECTORIES = 'directories'
    VIDEOS = 'videos'


class RENDERER:
    TV_SHOWS = COLLECTION.TV_SHOWS
    MOVIES = COLLECTION.MOVIES
    DIRECTORIES = 'directories'


class ENDPOINT:
    MEDIA = 'media'
    COLLECTION = MEDIA + '/<collection>'
    FILTER = COLLECTION + '/filter/<filter_name>/<filter_value>'
    MEDIA_PLAYED = COLLECTION + '/<media_id>/played/<uuid>'
    TV_SHOW_PLAYED = COLLECTION + '/<media_id>/<season>/<episode>/played'
    POPULAR = COLLECTION + '/popular/-1'
    MEDIA_DETAIL = COLLECTION + '/<media_id>'
    FILTER_COUNT = COLLECTION + '/filter/<filter_name>/count'
    USER = 'user'
    WATCHED = USER + '/watched/<uuid>'


class PROTOCOL:
    PLUGIN = 'plugin'


class REGEX:
    ROUTER_PARAMS = r"<.*?>"


class ROUTE:
    ROOT = '/'
    A_TO_Z = '/a_to_z/<collection>'
    A_TO_Z_SUBMENU = '/a_to_z/<collection>/<previous_letter>'
    SHOW_CACHED_MEDIA = '/show_cached_media/<collection>'
    NEXT_PAGE = '/next_page/<collection>/<url>'
    FILTER = '/filter/<collection>/<filter_type>/<filter_value>'
    SEARCH = '/search/<collection>'
    COMMAND = '/command/<what>'
    MEDIA_MENU = '/media/<collection>'
    MAIN_MENU = '/main_menu'
    GENRE_MENU = '/genre_menu/<collection>'
    SEARCH_RESULT = '/search_result/<collection>/<search_value>'
    SELECT_MOVIE_STREAM = '/select_stream/<collection>/<media_id>'
    PLAY_STREAM = '/play_stream/<ident>'
    SELECT_SEASON = '/select_season/<collection>/<media_id>'
    SELECT_EPISODE = '/select_episode/<collection>/<media_id>/<season_id>'
    SELECT_TV_SHOW_STREAM = '/select_tv_show_stream/<media_id>/<season_id>/<episode_id>'
    POPULAR = MEDIA_MENU + '/popular'
    CLEAR_CACHE = '/clear-cache'
    CLEAR_PATH = '/clear-path'
    WATCHED = '/watched'
    CHECK_PROVIDER_CREDENTIALS = '/check-provider-credentials'
    REFRESH_PROVIDER_TOKEN = '/refresh-provider-token'
    SET_PROVIDER_CREDENTIALS = '/set-provider-credentials'
    CSFD_TIPS = '/csfd_tips/<collection>'
    SEARCH_FOR_CSFD_TIPS = '/search_for_csfd_tip/<collection>/<item>'


class GITLAB_ENDPOINT:
    RELEASES = 'projects/<project_id>/releases'


class COMMAND:
    SEARCH = 'search'
    OPEN_SETTINGS = 'open-settings'


class STORAGE:
    COLLECTION = 'collection'
    MEDIA_LIST = 'media_list'
    PLUGIN_URL_HISTORY = 'plugin_url_history'
    PLUGIN_LAST_URL_ADDED = 'plugin_last_url_added'
    SELECTED_MEDIA_ID = 'selected_media_id'
    SERVICE = 'service'
    CLEARED_CACHE = 'cleared_cache'
    IS_OLD_KODI_SESSION = 'is_new_kodi_session'


class SERVICE:
    PLAYER_SERVICE = 'player_service'


class SERVICE_EVENT:
    PLAYBACK_STARTED = 'playback_started'
    PLAYBACK_STOPPED = 'playback_stopped'


class CACHE:
    EXPIRATION_TIME = 10
    EXPIRATION_TIME_BIGGER = 30
    PLUGIN_URL_HISTORY_LIMIT = 5


class DOWNLOAD_TYPE:
    VIDEO_STREAM = 'video_stream'
    FILE_DOWNLOAD = 'file_download'


class SETTINGS:
    VERSION = 'version'
    UUID = 'uuid'
    DEBUG = 'debug'
    PROVIDER_NAME = 'provider.name'
    PROVIDER_USERNAME = 'provider.username'
    PROVIDER_PASSWORD = 'provider.password'
    PROVIDER_TOKEN = 'provider.token'
    SHOW_CODEC = 'show_codec'
    SHOW_BITRATE = 'show_bitrate'
    SHOW_DURATION = 'show_duration'
    EXPLICIT_CONTENT = 'explicit_content'
    ADVANCED_CLEAR_CACHE = 'advanced.clear_cache'
    FILE_SIZE_SORT = 'file_size_sort'
    INSTALLATION_DATE = 'installation_date'
    LAST_VERSION_CHECK = 'last_version_check'
    LAST_VERSION_AVAILABLE = 'last_version_available'
    A_Z_THRESHOLD = 'a_z_threshold'
    IS_OUTDATED = 'is_outdated'
    VIP_DURATION = 'provider.vip_duration'
    LAST_VIP_CHECK = 'last_vip_check'


class STRINGS:
    STREAM_TITLE_BRACKETS = '[{}]'
    STREAM_BITRATE_BRACKETS = '[I]{}[/I]'
    AUDIO_INFO = '[{} {} {}]'
    SEASON_TITLE = '{} {}'
    BOLD = '[B]{}[/B]'
    TABLE_SPACES = '  '
    DATETIME = '%Y-%m-%d %H:%M:%S'
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
    A_TO_Z_TITLE = '{}  [I]({})[/I]'
    REGEX_BRACKETS = '[{}]'
    COLOR_GREEN = '[COLOR green]{}[/COLOR]'
    COLOR_RED = '[COLOR red]{}[/COLOR]'
    COLOR_BLUE = '[COLOR blue]{}[/COLOR]'
    NEW_LINE = '\n'
    PAIR = '{}: {}'
    PAIR_BOLD = BOLD + ': {}'
    EPISODE_TITLE = '{} - S{}E{}'
    VIP_INFO = '{} ({}: {})'


class CODEC:
    H265 = 'HEVC'
    H264 = 'H264'


class API_CODEC:
    H265 = 'h265'
    H264 = 'h264'


codecs = {
    API_CODEC.H265: CODEC.H265,
    API_CODEC.H264: CODEC.H264
}


class LANG:
    GENERAL = 30010
    SOURCE = 30011
    USERNAME = 30101
    PASSWORD = 30102
    PROVIDER = 30103
    WEBSHARE_CZ = 30104
    ADVANCED = 30012
    INSTALLATION_DATE = 30013
    INTERFACE = 30014
    SHOW_CODEC = 30115
    SHOW_BITRATE = 30116
    THRESHOLDS = 30118
    A_Z_THRESHOLD = 30119
    DEBUG = 30105
    MOVIES = 30200
    SERIES = 30201
    MAIN_MENU = 30202
    NEXT_PAGE = 30203
    SEARCH = 30204
    SEARCH_MEDIA = 30207
    SETTINGS = 30208
    GENRE = 30209
    A_Z = 30210
    POPULAR = 30211
    WATCHING_NOW = 30212
    ACTION = 30213
    ANIMATED = 30214
    ADVENTURE = 30215
    DOCUMENTARY = 30216
    DRAMA = 30217
    EROTIC = 30218
    FANTASY = 30219
    HISTORICAL = 30220
    HORROR = 30221
    MUSIC = 30222
    IMAX = 30223
    CATASTROPHIC = 30224
    COMEDY = 30225
    SHORT = 30226
    CRIME = 30227
    MUSICAL = 30228
    MYSTERIOUS = 30229
    EDUCATIONAL = 30230
    FAIRYTALE = 30231
    PORNOGRAPHIC = 30232
    PSYCHOLOGICAL = 30233
    JOURNALISTIC = 30234
    REALITY = 30235
    TRAVEL = 30236
    FAMILY = 30237
    ROMANTIC = 30238
    SCI_FI = 30239
    COMPETITION = 30240
    SPORTS = 30241
    STAND_UP = 30242
    TALK_SHOW = 30243
    TELENOVELA = 30244
    THRILLER = 30245
    MILITARY = 30246
    WESTERN = 30247
    BIOGRAPHICAL = 30248
    SELECT_A_MEDIA_SOURCE = 30250
    ZERO_NINE = 30251
    SEARCH_FOR_LETTERS = 30252
    CHOOSE_STREAM = 30253
    WATCH_HISTORY = 30254
    SEASON = 30920
    EPISODE = 30921
    MISSING_PROVIDER_CREDENTIALS = 30300
    SERVER_ERROR = 30301
    NOTHING_FOUND = 30302
    FOUND__NUM__RECORDS = 30303
    ACTIVATE_VIP = 30304
    NEWS_TITLE = 30305
    NEWS_TEXT = 30306
    NEW_VERSION_TITLE = 30307
    NEW_VERSION_TEXT = 30308
    PAGE_LIMIT = 30120
    PROVIDER_DETAILS = 30123
    VERIFY_LOGIN_INFORMATION = 30122
    TOKEN = 30121
    INCORRECT_PROVIDER_CREDENTIALS = 30124
    INFO = 30126
    TOKEN_REFRESHED = 30127
    CORRECT_PROVIDER_CREDENTIALS = 30128
    SHOW_DURATION = 30129
    VIP_REMAINS = 30130
    DAYS = 30132
    NOT_ACTIVE = 30133
    CSFD_TIPS = 30309


api_genres = {
    LANG.EROTIC: 'Erotic',
    LANG.PORNOGRAPHIC: 'Pornographic',
    LANG.ACTION: 'Action',
    LANG.ANIMATED: 'Animated',
    LANG.ADVENTURE: 'Adventure',
    LANG.BIOGRAPHICAL: 'Biographical',
    LANG.CATASTROPHIC: 'Catastrophic',
    LANG.COMEDY: 'Comedy',
    LANG.COMPETITION: 'Competition',
    LANG.CRIME: 'Crime',
    LANG.DOCUMENTARY: 'Documentary',
    LANG.FAIRYTALE: 'Fairytale',
    LANG.DRAMA: 'Drama',
    LANG.FAMILY: 'Family',
    LANG.FANTASY: 'Fantasy',
    LANG.HISTORICAL: 'Historical',
    LANG.HORROR: 'Horror',
    LANG.IMAX: 'IMAX',
    LANG.EDUCATIONAL: 'Educational',
    LANG.MUSIC: 'Music',
    LANG.JOURNALISTIC: 'Journalistic',
    LANG.MILITARY: 'Military',
    LANG.MUSICAL: 'Musical',
    LANG.MYSTERIOUS: 'Mysterious',
    LANG.PSYCHOLOGICAL: 'Psychological',
    LANG.REALITY: 'Reality',
    LANG.ROMANTIC: 'Romantic',
    LANG.SCI_FI: 'Sci-Fi',
    LANG.SHORT: 'Short',
    LANG.SPORTS: 'Sports',
    LANG.STAND_UP: 'Stand-Up',
    LANG.TALK_SHOW: 'Talk-Show',
    LANG.TELENOVELA: 'Telenovela',
    LANG.THRILLER: 'Thriller',
    LANG.TRAVEL: 'Travel',
    LANG.WESTERN: 'Western'
}

explicit_genres = [LANG.EROTIC, LANG.PORNOGRAPHIC]
