from typing import Tuple

from exactly_lib.definitions import misc_texts
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1

LineMatcher = MatcherWTrace[LineMatcherLine]

FIRST_LINE_NUMBER_DESCRIPTION = 'Line numbers start at {}.'.format(FIRST_LINE_NUMBER)

LINE_SEPARATOR_DESCRIPTION = """The line separator depends on the {} ('\\n', '\\r\\n', e.g.).""".format(
    misc_texts.CURRENT_OS
)
