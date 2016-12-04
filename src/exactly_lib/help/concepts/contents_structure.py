from exactly_lib.help.concepts.cross_reference import concept_cross_ref
from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME
from exactly_lib.help.utils.entity_documentation import EntityDocumentation, EntitiesHelp
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.structure.structures import para


class Name(tuple):
    def __new__(cls,
                singular: str,
                plural: str):
        return tuple.__new__(cls, (singular, plural))

    @property
    def singular(self) -> str:
        return self[0]

    @property
    def plural(self) -> str:
        return self[1]


class ConceptDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self,
                 name: Name):
        self._name = name

    def name(self) -> Name:
        return self._name

    def single_line_description(self) -> Text:
        return self.purpose().single_line_description

    def singular_name(self) -> str:
        return self.name().singular

    def cross_reference_target(self) -> EntityCrossReferenceId:
        return concept_cross_ref(self._name.singular)

    def purpose(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def summary_paragraphs(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return [para(self.purpose().single_line_description)]

    def see_also(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return []


class PlainConceptDocumentation(ConceptDocumentation):
    pass


class ConfigurationParameterDocumentation(ConceptDocumentation):
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
    return EntitiesHelp(CONCEPT_ENTITY_TYPE_NAME, concepts)


class ConceptsHelp(tuple):
    def __new__(cls,
                concepts: iter):
        """
        :type concepts: [`ConceptDocumentation`]
        """
        return tuple.__new__(cls, (list(concepts),))

    @property
    def all_concepts(self) -> list:
        """
        :type: [`ConceptDocumentation`]
        """
        return self[0]

    def lookup_by_name_in_singular(self, concept_name: str) -> ConceptDocumentation:
        matches = list(filter(lambda c: c.name().singular == concept_name, self.all_concepts))
        if not matches:
            raise KeyError('Not a concept: ' + concept_name)
        return matches[0]
