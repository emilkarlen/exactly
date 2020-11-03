from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Callable

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util import name_and_value
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.name import NameWithGenderWithFormatting
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents


class ElementDescriptionBase(ABC):
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


class PrimitiveDescription(ElementDescriptionBase, ABC):
    @abstractmethod
    def initial_argument(self, name: str) -> a.ArgumentUsage:
        pass

    @property
    @abstractmethod
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        pass


class PrimitiveDescriptionWithNameAsInitialSyntaxToken(PrimitiveDescription, ABC):
    def initial_argument(self, name: str) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        a.Constant(name))


class PrimitiveDescriptionWithSyntaxElementAsInitialSyntaxToken(PrimitiveDescription, ABC):
    def __init__(self, syntax_element_name: str):
        self._syntax_element_name = syntax_element_name

    def initial_argument(self, name: str) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        a.Named(self._syntax_element_name))


class ElementWithDescription(ABC):
    @abstractmethod
    def description(self) -> ElementDescriptionBase:
        pass


EXPR = TypeVar('EXPR')


class Primitive(Generic[EXPR], ElementWithDescription):
    def __init__(self,
                 parse_arguments: Callable[[TokenParser], EXPR],
                 syntax: PrimitiveDescription,
                 ):
        self.parse_arguments = parse_arguments
        self.syntax = syntax

    def description(self) -> ElementDescriptionBase:
        return self.syntax


class OperatorDescription(ElementDescriptionBase, ABC):
    pass


class InfixOperatorDescription(OperatorDescription, ABC):
    @property
    @abstractmethod
    def operand_evaluation__lazy__left_to_right(self) -> bool:
        pass


class InfixOperator(Generic[EXPR], ElementWithDescription):
    def __init__(self,
                 mk_expression: Callable[[Sequence[EXPR]], EXPR],
                 syntax: InfixOperatorDescription,
                 ):
        self.mk_expression = mk_expression
        self.syntax = syntax

    def description(self) -> InfixOperatorDescription:
        return self.syntax


class PrefixOperator(Generic[EXPR], ElementWithDescription):
    def __init__(self,
                 mk_expression: Callable[[EXPR], EXPR],
                 syntax: OperatorDescription,
                 ):
        self.mk_expression = mk_expression
        self.syntax = syntax

    def description(self) -> OperatorDescription:
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
                 primitives: Sequence[NameAndValue[Primitive[EXPR]]],
                 prefix_operators: Sequence[NameAndValue[PrefixOperator[EXPR]]],
                 infix_operators_in_order_of_increasing_precedence:
                 Sequence[Sequence[NameAndValue[InfixOperator[EXPR]]]],
                 description: Callable[[], SectionContents] = SectionContents.empty
                 ):
        self.concept = concept
        self.description = description
        self.mk_reference = mk_reference
        self.primitives__seq = primitives
        self.primitives = name_and_value.to_dict(primitives)
        self.prefix_operators__seq = prefix_operators
        self.prefix_operators = name_and_value.to_dict(prefix_operators)
        self.infix_ops_inc_precedence__seq = infix_operators_in_order_of_increasing_precedence
        self.infix_ops_inc_precedence = [
            name_and_value.to_dict(infix_ops_of_precedence)
            for infix_ops_of_precedence in infix_operators_in_order_of_increasing_precedence
        ]
