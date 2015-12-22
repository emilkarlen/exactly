class InvokationVariant:
    def __init__(self,
                 syntax: str,
                 description_rest: list):
        """
        :param syntax:
        :type description_rest: [ParagraphItem]
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
        :type description_rest: [ParagraphItem]
        :type invokation_variants: [InvokationVariant]
        """
        self.element_name = element_name
        self.invokation_variants = invokation_variants
        self.description_rest = description_rest


class Description:
    def __init__(self,
                 instruction_name: str):
        self._instruction_name = instruction_name

    def instruction_name(self) -> str:
        return self._instruction_name

    def single_line_description(self) -> str:
        raise NotImplementedError()

    def main_description_rest(self) -> list:
        """
        :return: [ParagraphItem]
        """
        return []

    def invokation_variants(self) -> list:
        """
        :return: [InvokationVariant]
        """
        return []

    def syntax_element_descriptions(self) -> list:
        """
        :return: [SyntaxElementDescription]
        """
        return []


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
        self.__syntax_element_descriptions = syntax_element_descriptions

    def single_line_description(self) -> str:
        return self.__single_line_description

    def main_description_rest(self) -> str:
        return self.__main_description_rest

    def invokation_variants(self) -> list:
        return self.__invokation_variants

    def syntax_element_descriptions(self) -> iter:
        return self.__syntax_element_descriptions
