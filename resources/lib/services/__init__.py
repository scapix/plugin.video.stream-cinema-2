from resources.lib.const import STORAGE
from resources.lib.kodilogging import service_logger
from resources.lib.storage.storage import storage


class Service:
    SERVICE_NAME = ''
    _event_callbacks = {}

    @staticmethod
    def storage():
        return storage.get(STORAGE.SERVICE)

    def _is_allowed(self, service_event):
        is_allowed = self.storage().get(self.SERVICE_NAME) == service_event
        if is_allowed:
            service_logger.debug("Event emission came from my master. Proceeding.")
            self._clear_event()
        return is_allowed

    def _clear_event(self):
        self.storage()[self.SERVICE_NAME] = None

    def emit(self, service_event):
        if self._is_allowed(service_event):
            service_logger.debug('Emitting service event %s' % service_event)
            self._event_callbacks[service_event]()
