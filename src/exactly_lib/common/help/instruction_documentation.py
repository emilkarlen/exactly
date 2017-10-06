from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, SeeAlsoSet


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

    def see_also_items(self) -> list:
        """
        :rtype: [`SeeAlsoItem`]
        """
        return [CrossReferenceIdSeeAlsoItem(x) for x in self._see_also_cross_refs()]

    def see_also_set(self) -> SeeAlsoSet:
        return SeeAlsoSet(self._see_also_cross_refs())

    def _see_also_cross_refs(self) -> list:
        """
        :rtype [`CrossReferenceId`]
        """
        return []
