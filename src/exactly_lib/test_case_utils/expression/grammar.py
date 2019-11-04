from typing import Mapping, Optional, Sequence, TypeVar, Generic, Callable

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name import NameWithGenderWithFormatting
from exactly_lib.util.textformat.structure.core import ParagraphItem


class SimpleExpressionDescription:
    def __init__(self,
                 argument_usage_list: Sequence[a.ArgumentUsage],
                 description_rest: Sequence[ParagraphItem],
                 see_also_targets: Sequence[SeeAlsoTarget] = ()):
        self.argument_usage_list = argument_usage_list
        self.description_rest = description_rest
        self.see_also_targets = list(see_also_targets)


EXPR = TypeVar('EXPR')


class SimpleExpression(Generic[EXPR]):
    def __init__(self,
                 parse_arguments: Callable[[TokenParser], EXPR],
                 syntax: SimpleExpressionDescription):
        self.parse_arguments = parse_arguments
        self.syntax = syntax


class OperatorExpressionDescription:
    def __init__(self,
                 description_rest: Sequence[ParagraphItem],
                 see_also_targets: Sequence[SeeAlsoTarget] = ()):
        self.description_rest = description_rest
        self.see_also_targets = list(see_also_targets)


class ComplexExpression(Generic[EXPR]):
    def __init__(self,
                 mk_complex: Callable[[Sequence[EXPR]], EXPR],
                 syntax: OperatorExpressionDescription):
        self.mk_complex = mk_complex
        self.syntax = syntax


class PrefixExpression(Generic[EXPR]):
    def __init__(self,
                 mk_expression: Callable[[EXPR], EXPR],
                 syntax: OperatorExpressionDescription):
        self.mk_expression = mk_expression
        self.syntax = syntax


class Concept:
    def __init__(self,
                 name: NameWithGenderWithFormatting,
                 type_system_type_name: str,
                 syntax_element_name: a.Named):
        self.type_system_type_name = type_system_type_name
        self.name = name
        self.syntax_element = syntax_element_name


class Grammar(Generic[EXPR]):
    def __init__(self,
                 concept: Concept,
                 mk_reference: Callable[[str], EXPR],
                 simple_expressions: Mapping[str, SimpleExpression[EXPR]],
                 complex_expressions: Mapping[str, ComplexExpression[EXPR]],
                 prefix_expressions: Optional[Mapping[str, PrefixExpression[EXPR]]] = None):
        self.concept = concept
        self.mk_reference = mk_reference
        self.simple_expressions = simple_expressions
        self.complex_expressions = complex_expressions
        self.prefix_expressions = prefix_expressions if prefix_expressions else {}
