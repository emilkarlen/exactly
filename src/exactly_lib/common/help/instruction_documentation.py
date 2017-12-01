from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.util.textformat.structure.core import StringText


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

    @property
    def instruction_name_text(self) -> StringText:
        return syntax_text(self._instruction_name)

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

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []
