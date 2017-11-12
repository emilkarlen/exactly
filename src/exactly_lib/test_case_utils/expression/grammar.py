from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name import Name


class SimpleExpressionDescription:
    def __init__(self,
                 argument_usage_list: list,
                 description_rest: list,
                 see_also_targets: list = ()):
        self.argument_usage_list = argument_usage_list
        self.description_rest = description_rest
        self.see_also_targets = list(see_also_targets)


class SimpleExpression:
    def __init__(self,
                 parse_arguments,
                 syntax: SimpleExpressionDescription):
        """
        :param parse_arguments: TokenParserPrime -> Expr
        """
        self.parse_arguments = parse_arguments
        self.syntax = syntax


class OperatorExpressionDescription:
    def __init__(self,
                 description_rest: list,
                 see_also_targets: list = ()):
        self.description_rest = description_rest
        self.see_also_targets = list(see_also_targets)


class ComplexExpression:
    def __init__(self,
                 mk_complex,
                 syntax: OperatorExpressionDescription):
        """
        :param mk_complex: [Expr] -> Expr
        """
        self.mk_complex = mk_complex
        self.syntax = syntax


class PrefixExpression:
    def __init__(self,
                 mk_expression,
                 syntax: OperatorExpressionDescription):
        """
        :param mk_expression: Expr -> Expr
        """
        self.mk_expression = mk_expression
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
                 complex_expressions: dict,
                 prefix_expressions: dict = None):
        """
        :param mk_reference: str -> Expr
        :param simple_expressions: dict str -> :class:`SimpleExpression`
        :param complex_expressions: dict str -> :class:`ComplexExpression`
        :param prefix_expressions: dict str -> :class:`PrefixExpression`
        """
        self.concept = concept
        self.mk_reference = mk_reference
        self.simple_expressions = simple_expressions
        self.complex_expressions = complex_expressions
        self.prefix_expressions = prefix_expressions if prefix_expressions else {}
