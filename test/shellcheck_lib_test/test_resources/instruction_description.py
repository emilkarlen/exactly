from shellcheck_lib.general.textformat import parse as text_parse
from shellcheck_lib.test_case.help.instruction_description import Description


class DescriptionWithConstantValues(Description):
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
