import logging

import xbmc

from resources.lib.utils.kodiutils import get_setting_as_bool, get_info
from resources.lib.const import SETTINGS

levels = {
    'CRITICAL': xbmc.LOGFATAL,
    'ERROR': xbmc.LOGERROR,
    'WARNING': xbmc.LOGWARNING,
    'INFO': xbmc.LOGINFO,
    'DEBUG': xbmc.LOGDEBUG,
    'NOTSET': xbmc.LOGNONE,
}


class KodiLogHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        formatter = logging.Formatter('[%(name)s] %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        if get_setting_as_bool(SETTINGS.DEBUG):
            xbmc.log(self.format(record), levels[record.levelname])

    def flush(self):
        pass


def setup_root_logger():
    root_logger = logging.getLogger()
    root_logger.handlers = [KodiLogHandler()]
    root_logger.setLevel(logging.DEBUG)


logging.basicConfig()
logger = logging.getLogger(get_info('id'))
service_logger = logging.getLogger(get_info('id') + '.service')
