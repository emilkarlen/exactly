from exactly_lib.help.utils.entity_documentation import EntitiesHelp, \
    command_line_names_as_singular_name, EntityDocumentationBase
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, CrossReferenceId
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.name import Name, name_with_plural_s
from exactly_lib.util.textformat.structure.core import Text
from exactly_lib.util.textformat.structure.structures import para

CONCEPT_ENTITY_TYPE_NAMES = command_line_names_as_singular_name(name_with_plural_s('concept'))


class ConceptDocumentation(EntityDocumentationBase):
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

    def single_line_description(self) -> Text:
        return self._info.single_line_description

    def singular_name(self) -> str:
        return self.name().singular

    def cross_reference_target(self) -> CrossReferenceId:
        return self._info.cross_reference_target

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


def concepts_help(concepts: iter) -> EntitiesHelp:
    """
    :param concepts: [ConceptDocumentation]
    """
    return EntitiesHelp(CONCEPT_ENTITY_TYPE_NAMES,
                        concepts)
