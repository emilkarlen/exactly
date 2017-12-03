from exactly_lib.help.contents_structure.entity import EntityTypeHelp, \
    EntityDocumentation
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.name import Name
from exactly_lib.util.textformat.structure.structures import para


class ConceptDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, info: SingularAndPluralNameAndCrossReferenceId):
        super().__init__(info)
        self._info = info

    @property
    def name_and_cross_ref_target(self) -> SingularAndPluralNameAndCrossReferenceId:
        return self._info

    def name(self) -> Name:
        return self._info.name

    def purpose(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def summary_paragraphs(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return [para(self.purpose().single_line_description)]

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []


def concepts_help(concepts: iter) -> EntityTypeHelp:
    """
    :param concepts: [ConceptDocumentation]
    """
    return EntityTypeHelp(CONCEPT_ENTITY_TYPE_NAMES,
                          concepts)
