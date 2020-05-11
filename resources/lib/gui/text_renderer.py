from resources.lib.const import STRINGS
from resources.lib.utils.kodiutils import apply_strings


class TextRenderer:
    @staticmethod
    def highlight(text):
        return apply_strings([text], STRINGS.BOLD, STRINGS.COLOR_BLUE)

    @staticmethod
    def bold(text):
        return apply_strings([text], STRINGS.BOLD)

    @staticmethod
    def make_pair(pair_format, text):
        return pair_format.format(*text)
