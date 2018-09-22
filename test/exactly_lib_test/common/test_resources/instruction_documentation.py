from typing import List, Sequence

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.util.textformat import parse as text_parse
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import Section
from exactly_lib_test.common.test_resources import syntax_parts


class InstructionDocumentationWithConstantValues(InstructionDocumentation, WithAssertPhasePurpose):
    def __init__(self,
                 instruction_name: str,
                 single_line_description: str,
                 main_description_rest: str,
                 invokation_variants: List[InvokationVariant],
                 syntax_element_descriptions: Sequence[SyntaxElementDescription] = (),
                 main_description_rest_sub_sections: Sequence[Section] = ()):
        super().__init__(instruction_name)
        self.__single_line_description = single_line_description
        self.__main_description_rest = main_description_rest
        self.__invokation_variants = invokation_variants
        self.__syntax_element_descriptions = list(syntax_element_descriptions)
        self.__main_description_rest_sub_sections = main_description_rest_sub_sections

    def single_line_description(self) -> str:
        return self.__single_line_description

    def main_description_rest(self) -> List[ParagraphItem]:
        return text_parse.normalize_and_parse(self.__main_description_rest)

    def main_description_rest_sub_sections(self) -> Sequence[Section]:
        return self.__main_description_rest_sub_sections

    def invokation_variants(self) -> List[InvokationVariant]:
        return self.__invokation_variants

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return self.__syntax_element_descriptions


def instruction_documentation(instruction_name: str) -> InstructionDocumentation:
    return InstructionDocumentationWithConstantValues(instruction_name,
                                                      'single line description',
                                                      'main description rest',
                                                      syntax_parts.INVOKATION_VARIANTS,
                                                      syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS)
