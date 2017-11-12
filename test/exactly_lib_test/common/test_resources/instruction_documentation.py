from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.util.textformat import parse as text_parse
from exactly_lib_test.common.test_resources import syntax_parts


class InstructionDocumentationWithConstantValues(InstructionDocumentation):
    def __init__(self,
                 instruction_name: str,
                 single_line_description: str,
                 main_description_rest: str,
                 invokation_variants: list,
                 syntax_element_descriptions: iter = ()):
        """
        :param invokation_variants: [InvokationVariant]
        :param syntax_element_descriptions: [SyntaxElementDescription]
        """
        super().__init__(instruction_name)
        self.__single_line_description = single_line_description
        self.__main_description_rest = main_description_rest
        self.__invokation_variants = invokation_variants
        self.__syntax_element_descriptions = list(syntax_element_descriptions)

    def single_line_description(self) -> str:
        return self.__single_line_description

    def main_description_rest(self) -> list:
        return text_parse.normalize_and_parse(self.__main_description_rest)

    def invokation_variants(self) -> list:
        return self.__invokation_variants

    def syntax_element_descriptions(self) -> iter:
        return self.__syntax_element_descriptions


def instruction_documentation(instruction_name: str) -> InstructionDocumentation:
    return InstructionDocumentationWithConstantValues(instruction_name,
                                                      'single line description',
                                                      'main description rest',
                                                      syntax_parts.INVOKATION_VARIANTS,
                                                      syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS)
