from typing import Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.util.textformat.structure.document import SectionContents


class CustomSymbolDocumentation:
    def __init__(self,
                 single_line_description: str,
                 documentation: SectionContents,
                 see_also: Sequence[SeeAlsoTarget] = (),
                 ):
        self.single_line_description = single_line_description
        self.documentation = documentation
        self.see_also = see_also
