from exactly_lib.help_texts.name_and_cross_ref import Name
from exactly_lib.util.cli_syntax.elements import argument as a


class SimpleExpressionDescription:
    def __init__(self,
                 argument_usage_list: list,
                 description_rest: list):
        self.argument_usage_list = argument_usage_list
        self.description_rest = description_rest


class SimpleExpression:
    def __init__(self,
                 parse_arguments,
                 syntax: SimpleExpressionDescription):
        """
        :param parse_arguments: TokenParserPrime -> Expr
        """
        self.parse_arguments = parse_arguments
        self.syntax = syntax


class ComplexExpressionDescription:
    def __init__(self,
                 description_rest: list):
        self.description_rest = description_rest


class ComplexExpression:
    def __init__(self,
                 mk_complex,
                 syntax: ComplexExpressionDescription):
        """
        :param mk_complex: [NamedElementResolver] -> Expr
        """
        self.mk_complex = mk_complex
        self.syntax = syntax


class Concept:
    def __init__(self,
                 name: Name,
                 type_system_type_name: str,
                 syntax_element_name: a.Named):
        self.type_system_type_name = type_system_type_name
        self.name = name
        self.syntax_element = syntax_element_name


class Grammar:
    def __init__(self,
                 concept: Concept,
                 mk_reference,
                 simple_expressions: dict,
                 complex_expressions: dict):
        """
        :param mk_reference: str -> NamedElementResolver
        :param simple_expressions: dict str -> :class:`SimpleExpression`
        :param complex_expressions: dict str -> :class:`ComplexExpression`
        """
        self.concept = concept
        self.mk_reference = mk_reference
        self.simple_expressions = simple_expressions
        self.complex_expressions = complex_expressions
