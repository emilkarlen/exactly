from abc import ABC, abstractmethod
from typing import Optional, Sequence, TypeVar, Generic, Callable

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util import name_and_value
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name import NameWithGenderWithFormatting
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem


class ExpressionDescriptionBase(ABC):
    @property
    @abstractmethod
    def description_rest(self) -> Sequence[ParagraphItem]:
        pass

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return ()

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return ()


class SimpleExpressionDescription(ExpressionDescriptionBase, ABC):
    @property
    @abstractmethod
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        pass


class ExpressionWithDescription(ABC):
    @abstractmethod
    def description(self) -> ExpressionDescriptionBase:
        pass


EXPR = TypeVar('EXPR')


class SimpleExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 parse_arguments: Callable[[TokenParser], EXPR],
                 syntax: SimpleExpressionDescription):
        self.parse_arguments = parse_arguments
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


class OperatorExpressionDescription(ExpressionDescriptionBase, ABC):
    pass


class ComplexExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 mk_complex: Callable[[Sequence[EXPR]], EXPR],
                 syntax: OperatorExpressionDescription):
        self.mk_complex = mk_complex
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


class PrefixExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 mk_expression: Callable[[EXPR], EXPR],
                 syntax: OperatorExpressionDescription):
        self.mk_expression = mk_expression
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


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
                 simple_expressions: Sequence[NameAndValue[SimpleExpression[EXPR]]],
                 complex_expressions: Sequence[NameAndValue[ComplexExpression[EXPR]]],
                 prefix_expressions: Optional[Sequence[NameAndValue[PrefixExpression[EXPR]]]] = None):
        self.concept = concept
        self.mk_reference = mk_reference
        self.simple_expressions_list = simple_expressions
        self.simple_expressions = name_and_value.to_dict(simple_expressions)
        self.complex_expressions_list = complex_expressions
        self.complex_expressions = name_and_value.to_dict(complex_expressions)
        self.prefix_expressions = name_and_value.to_dict(prefix_expressions) if prefix_expressions else {}
        self.prefix_expressions_list = prefix_expressions if prefix_expressions else ()
