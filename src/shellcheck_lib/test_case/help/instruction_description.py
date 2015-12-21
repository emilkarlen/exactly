class InvokationVariant:
    def __init__(self,
                 syntax: str,
                 description_rest: str):
        self.syntax = syntax
        self.description_rest = description_rest


class SyntaxElementDescription:
    def __init__(self,
                 element_name: str,
                 description_rest: str,
                 invokation_variants: list):
        self.element_name = element_name
        self.invokation_variants = invokation_variants
        self.description_rest = description_rest


class Description:
    def __init__(self,
                 single_line_description: str,
                 main_description_rest: str,
                 invokation_variants: list,
                 syntax_element_descriptions: iter = ()):
        """
        :param invokation_variants: [InvokationVariant]
        :param syntax_element_descriptions: [SyntaxElementDescription]
        """
        self.__single_line_description = single_line_description
        self.__main_description_rest = main_description_rest
        self.__invokation_variants = invokation_variants
        self.__syntax_element_descriptions = syntax_element_descriptions

    @property
    def single_line_description(self) -> str:
        return self.__single_line_description

    @property
    def main_description_rest(self) -> str:
        return self.__main_description_rest

    @property
    def invokation_variants(self) -> list:
        return self.__invokation_variants

    @property
    def syntax_element_descriptions(self) -> iter:
        return self.__syntax_element_descriptions
