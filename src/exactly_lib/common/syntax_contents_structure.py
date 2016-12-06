class InvokationVariant:
    def __init__(self,
                 syntax: str,
                 description_rest: list = None):
        """
        :param syntax:
        :type description_rest: [`ParagraphItem`]
        """
        self.syntax = syntax
        self.description_rest = [] if description_rest is None else description_rest


class SyntaxElementDescription:
    def __init__(self,
                 element_name: str,
                 description_rest: list,
                 invokation_variants: list = None):
        """
        :param element_name:
        :type description_rest: [`ParagraphItem`]
        :type invokation_variants: [`InvokationVariant`]
        """
        self.element_name = element_name
        self.invokation_variants = [] if invokation_variants is None else invokation_variants
        self.description_rest = description_rest
