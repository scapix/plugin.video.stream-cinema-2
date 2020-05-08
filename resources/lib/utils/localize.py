"""
    Localization utilities.
"""
import re

from resources.lib.utils.kodiutils import get_string

LANG_PATTERN = re.compile(r'\$(\d{5})')


def templated_string(self, text):
    """Replaces Localization templates in the given string.

    Pattern: $300123 is replaced with the string ID 300123 from .po file.
    """
    def replacer(match):
        int_repr = int(match.group(1))
        return get_string(int_repr)
    return re.sub(LANG_PATTERN, replacer, text)
