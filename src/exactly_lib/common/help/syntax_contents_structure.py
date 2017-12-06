from exactly_lib.help_texts.argument_rendering import cl_syntax


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


def invokation_variant_from_string(syntax: str,
                                   description_rest: list = None) -> InvokationVariant:
    return InvokationVariant(syntax,
                             description_rest)


def invokation_variant_from_args(argument_usages: list,
                                 description_rest: list = None) -> InvokationVariant:
    return InvokationVariant(cl_syntax.cl_syntax_for_args(argument_usages),
                             description_rest)


class SyntaxElementDescription(tuple):
    def __new__(cls,
                element_name: str,
                description_rest: list,
                invokation_variants: list = None):
        """
        :type description_rest: [`ParagraphItem`]
        :type invokation_variants: [`InvokationVariant`]
        """
        return tuple.__new__(cls, (element_name,
                                   description_rest,
                                   [] if invokation_variants is None else invokation_variants))

    @property
    def element_name(self) -> str:
        return self[0]

    @property
    def description_rest(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self[1]

    @property
    def invokation_variants(self) -> list:
        """
        :rtype: [`InvokationVariant`]
        """
        return self[2]
