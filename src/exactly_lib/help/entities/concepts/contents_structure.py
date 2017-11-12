from exactly_lib.help.utils.entity_documentation import EntityDocumentation, EntitiesHelp
from exactly_lib.help_texts import entity_names
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, CrossReferenceId
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.name import Name
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.structure.structures import para


class ConceptDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, info: SingularAndPluralNameAndCrossReferenceId):
        self._info = info

    def name(self) -> Name:
        return self._info.name

    def single_line_description(self) -> Text:
        return self._info.single_line_description

    def singular_name(self) -> str:
        return self.name().singular

    def cross_reference_target(self) -> CrossReferenceId:
        return self._info.cross_reference_target

    @property
    def is_configuration_parameter(self) -> bool:
        raise NotImplementedError('abstract method')

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


class PlainConceptDocumentation(ConceptDocumentation):
    @property
    def is_configuration_parameter(self) -> bool:
        return False


class ConfigurationParameterDocumentation(ConceptDocumentation):
    @property
    def is_configuration_parameter(self) -> bool:
        return True

    def default_value_str(self) -> str:
        raise NotImplementedError()

    def default_value_para(self) -> ParagraphItem:
        return para(self.default_value_str())

    def summary_paragraphs(self) -> list:
        return [para(self.purpose().single_line_description),
                para('Default value: ' + self.default_value_str())]


class ConceptDocumentationVisitor:
    def visit(self, x: ConceptDocumentation):
        if isinstance(x, PlainConceptDocumentation):
            return self.visit_plain_concept(x)
        if isinstance(x, ConfigurationParameterDocumentation):
            return self.visit_configuration_parameter(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ConceptDocumentation)))

    def visit_plain_concept(self, x: PlainConceptDocumentation):
        raise NotImplementedError()

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation):
        raise NotImplementedError()


def concepts_help(concepts: iter) -> EntitiesHelp:
    """
    :param concepts: [ConceptDocumentation]
    """
    return EntitiesHelp(entity_names.CONCEPT_ENTITY_TYPE_NAME,
                        entity_names.CONCEPT_ENTITY_TYPE_NAME,
                        concepts)
