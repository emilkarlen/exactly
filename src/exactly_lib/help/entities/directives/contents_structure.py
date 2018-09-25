from typing import List, Iterable, Sequence, Optional

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.all_entity_types import DIRECTIVE_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.directives import DirectiveInfo
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, \
    EntityDocumentation
from exactly_lib.section_document.model import SectionContents


class DirectiveDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, info: DirectiveInfo):
        super().__init__(info)
        self._info = info

    @property
    def info(self) -> DirectiveInfo:
        return self._info

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        raise NotImplementedError('abstract method')

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        raise NotImplementedError('abstract method')

    def description(self) -> Optional[SectionContents]:
        raise NotImplementedError('abstract method')

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        return []


def directives_help(directives: Iterable[DirectiveDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(DIRECTIVE_ENTITY_TYPE_NAMES,
                          directives)
