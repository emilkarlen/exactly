from typing import List, Iterable

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, \
    SingularAndPluralAndAcronymNameAndCrossReferenceId
from exactly_lib.definitions.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, \
    EntityDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.name import NameWithGenderWithFormatting
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import para


class ConceptDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, info: SingularAndPluralAndAcronymNameAndCrossReferenceId):
        super().__init__(info)
        self._info = info
        self._name_with_formatting = formatting.concept_name_with_formatting(info.name)

    @property
    def name_and_cross_ref_target(self) -> SingularAndPluralNameAndCrossReferenceId:
        return self._info

    def name(self) -> NameWithGenderWithFormatting:
        return self._name_with_formatting

    def acronym(self) -> str:
        return self._info.acronym

    def purpose(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def summary_paragraphs(self) -> List[ParagraphItem]:
        return [para(self.purpose().single_line_description)]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        return []


def concepts_help(concepts: Iterable[ConceptDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(CONCEPT_ENTITY_TYPE_NAMES,
                          concepts)
