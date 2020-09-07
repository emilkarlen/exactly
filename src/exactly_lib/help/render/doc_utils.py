from typing import List

from exactly_lib.common.help.headers import DESCRIPTION__HEADER__UPPERCASE, SYNOPSIS_TEXT
from exactly_lib.util.textformat.structure import document as doc


def synopsis_section(contents: doc.SectionContents) -> doc.Section:
    return doc.Section(SYNOPSIS_TEXT, contents)


def description_section(contents: doc.SectionContents) -> doc.Section:
    return doc.Section(DESCRIPTION__HEADER__UPPERCASE, contents)


def description_section_if_non_empty(contents: doc.SectionContents) -> List[doc.Section]:
    if contents.is_empty:
        return []
    else:
        return [description_section(contents)]
