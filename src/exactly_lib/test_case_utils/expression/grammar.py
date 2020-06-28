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


class PrimitiveExpressionDescription(ExpressionDescriptionBase, ABC):
    @abstractmethod
    def initial_argument(self, name: str) -> a.ArgumentUsage:
        pass

    @property
    @abstractmethod
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        pass


class PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken(PrimitiveExpressionDescription, ABC):
    def initial_argument(self, name: str) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        a.Constant(name))


class PrimitiveExpressionDescriptionWithSyntaxElementAsInitialSyntaxToken(PrimitiveExpressionDescription, ABC):
    def __init__(self, syntax_element_name: str):
        self._syntax_element_name = syntax_element_name

    def initial_argument(self, name: str) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        a.Named(self._syntax_element_name))


class ExpressionWithDescription(ABC):
    @abstractmethod
    def description(self) -> ExpressionDescriptionBase:
        pass


EXPR = TypeVar('EXPR')


class PrimitiveExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 parse_arguments: Callable[[TokenParser], EXPR],
                 syntax: PrimitiveExpressionDescription,
                 ):
        self.parse_arguments = parse_arguments
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


class OperatorExpressionDescription(ExpressionDescriptionBase, ABC):
    pass


class InfixOpExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 mk_complex: Callable[[Sequence[EXPR]], EXPR],
                 syntax: OperatorExpressionDescription,
                 ):
        self.mk_complex = mk_complex
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


class PrefixOpExpression(Generic[EXPR], ExpressionWithDescription):
    def __init__(self,
                 mk_expression: Callable[[EXPR], EXPR],
                 syntax: OperatorExpressionDescription,
                 ):
        self.mk_expression = mk_expression
        self.syntax = syntax

    def description(self) -> ExpressionDescriptionBase:
        return self.syntax


class Concept:
    def __init__(self,
                 name: NameWithGenderWithFormatting,
                 type_system_type_name: str,
                 syntax_element_name: a.Named,
                 ):
        self.type_system_type_name = type_system_type_name
        self.name = name
        self.syntax_element = syntax_element_name


class Grammar(Generic[EXPR]):
    def __init__(self,
                 concept: Concept,
                 mk_reference: Callable[[str], EXPR],
                 primitive_expressions: Sequence[NameAndValue[PrimitiveExpression[EXPR]]],
                 infix_op_expressions: Sequence[NameAndValue[InfixOpExpression[EXPR]]],
                 prefix_op_expressions: Optional[Sequence[NameAndValue[PrefixOpExpression[EXPR]]]] = None,
                 ):
        self.concept = concept
        self.mk_reference = mk_reference
        self.primitive_expressions_list = primitive_expressions
        self.primitive_expressions = name_and_value.to_dict(primitive_expressions)
        self.infix_op_expressions_list = infix_op_expressions
        self.infix_op_expressions = name_and_value.to_dict(infix_op_expressions)
        self.prefix_op_expressions = name_and_value.to_dict(prefix_op_expressions) if prefix_op_expressions else {}
        self.prefix_op_expressions_list = prefix_op_expressions if prefix_op_expressions else ()
