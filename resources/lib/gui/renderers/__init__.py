from resources.lib.utils.kodiutils import router_url_for


class Renderer(object):
    def __init__(self, router):
        self._router = router

    @property
    def handle(self):
        return self._router.handle

    def _url_for(self, *args, **kwargs):
        return router_url_for(self._router, *args, **kwargs)
