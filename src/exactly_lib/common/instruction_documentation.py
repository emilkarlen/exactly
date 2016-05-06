from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs


class InvokationVariant:
    def __init__(self,
                 syntax: str,
                 description_rest: list):
        """
        :param syntax:
        :type description_rest: [`ParagraphItem`]
        """
        self.syntax = syntax
        self.description_rest = description_rest


class SyntaxElementDescription:
    def __init__(self,
                 element_name: str,
                 description_rest: list,
                 invokation_variants: list):
        """
        :param element_name:
        :type description_rest: [`ParagraphItem`]
        :type invokation_variants: [`InvokationVariant`]
        """
        self.element_name = element_name
        self.invokation_variants = invokation_variants
        self.description_rest = description_rest


class InstructionDocumentation:
    """
    Reference documentation about an instruction,
    à la man page.
    """

    def __init__(self,
                 instruction_name: str):
        self._instruction_name = instruction_name

    def instruction_name(self) -> str:
        return self._instruction_name

    def description(self) -> Description:
        return Description(docs.text(self.single_line_description()),
                           self.main_description_rest())

    def single_line_description(self) -> str:
        raise NotImplementedError()

    def main_description_rest(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        return []

    def invokation_variants(self) -> list:
        """
        :rtype [`InvokationVariant`]
        """
        return []

    def syntax_element_descriptions(self) -> list:
        """
        :rtype [`SyntaxElementDescription`]
        """
        return []

    def see_also(self) -> list:
        """
        :rtype [`CrossReference`]
        """
        return []
