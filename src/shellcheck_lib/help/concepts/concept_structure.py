from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import para


class Name(tuple):
    def __new__(cls,
                singular: str):
        return tuple.__new__(cls, (singular,))

    @property
    def singular(self) -> str:
        return self[0]


class ConceptDocumentation:
    def __init__(self,
                 name: Name):
        self._name = name

    def name(self) -> Name:
        return self._name

    def purpose(self) -> Description:
        raise NotImplementedError()

    def summary_paragraphs(self) -> list:
        """
        :rtype: [ParagraphItem]
        """
        return [para(self.purpose().single_line_description)]


class PlainConceptDocumentation(ConceptDocumentation):
    pass


class ConfigurationParameterDocumentation(ConceptDocumentation):
    def default_value_str(self) -> str:
        """
        :rtype: [ParagraphItem]
        """
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
        raise ValueError('%s is not an instance of %s' % (str(x), str(ConceptDocumentation)))

    def visit_plain_concept(self, x: PlainConceptDocumentation):
        raise NotImplementedError()

    def visit_configuration_parameter(self, x: ConfigurationParameterDocumentation):
        raise NotImplementedError()
