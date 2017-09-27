class InvokationVariant(tuple):
    def __new__(cls,
                syntax: str,
                description_rest: list = None):
        """
        :type description_rest: [`ParagraphItem`]
        """
        return tuple.__new__(cls, (syntax, [] if description_rest is None else description_rest))

    @property
    def syntax(self) -> str:
        return self[0]

    @property
    def description_rest(self) -> list:
        return self[1]


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
