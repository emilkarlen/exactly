from typing import Sequence

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression.grammar import OperatorExpressionDescription
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name import NameWithGenderWithFormatting, NameWithGender
from exactly_lib.util.textformat.structure.core import ParagraphItem


class Expr:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class RefExpr(Expr):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.symbol_name)


class PrefixExprBase(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               str(self.expression))


class PrefixExprP(PrefixExprBase):
    pass


class PrefixExprQ(PrefixExprBase):
    pass


class SimpleExpr(Expr):
    pass


class SimpleWithArg(SimpleExpr):
    def __init__(self, argument: str):
        self.argument = argument

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               repr(self.argument))


class SimpleSansArg(SimpleExpr):
    def __str__(self):
        return self.__class__.__name__


class ComplexExpr(Expr):
    def __init__(self, expressions: Sequence[Expr]):
        self.expressions = expressions

    def __str__(self):
        return '{}[{}]'.format(self.__class__.__name__,
                               ', '.join(map(str, self.expressions)))


class ComplexA(ComplexExpr):
    pass


class ComplexB(ComplexExpr):
    pass


def parse_simple_with_arg(parser: TokenParser) -> SimpleWithArg:
    token = parser.consume_mandatory_token('failed parse of simple expression with arg')
    return SimpleWithArg(token.string)


def parse_simple_sans_arg(parser: TokenParser) -> SimpleSansArg:
    return SimpleSansArg()


CROSS_REF_ID = CustomCrossReferenceId('custom-target')

SIMPLE_WITH_ARG = 'simple_with_arg'
SIMPLE_SANS_ARG = 'simple_sans_arg'

NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME = 'not/a/simple/expr/name/and/not/a/valid/symbol/name'

PREFIX_P = '!'
PREFIX_Q = 'prefix_q'

COMPLEX_A = 'complex_a'
COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME = '||'

CONCEPT = grammar.Concept(
    NameWithGenderWithFormatting(
        NameWithGender('a',
                       'concept singular',
                       'concept plural')),
    'type-system-name',
    a.Named('SYNTAX-ELEMENT-NAME'))


class ConstantSimpleExprDescription(grammar.SimpleExpressionDescription):
    def __init__(self,
                 argument_usage_list: Sequence[a.ArgumentUsage],
                 description_rest: Sequence[ParagraphItem],
                 see_also_targets: Sequence[SeeAlsoTarget] = ()):
        self._argument_usage_list = argument_usage_list
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._argument_usage_list

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


class ConstantOperatorExpressionDescription(OperatorExpressionDescription):
    def __init__(self,
                 description_rest: Sequence[ParagraphItem],
                 see_also_targets: Sequence[SeeAlsoTarget] = ()):
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


SIMPLE_EXPRESSIONS = {
    SIMPLE_WITH_ARG: grammar.SimpleExpression(parse_simple_with_arg,
                                              ConstantSimpleExprDescription([], [],
                                                                            [CROSS_REF_ID])),
    SIMPLE_SANS_ARG: grammar.SimpleExpression(parse_simple_sans_arg,
                                              ConstantSimpleExprDescription([], [])),
}

PREFIX_EXPRESSIONS = {
    PREFIX_P: grammar.PrefixExpression(PrefixExprP,
                                       ConstantOperatorExpressionDescription([])),
    PREFIX_Q: grammar.PrefixExpression(PrefixExprQ,
                                       ConstantOperatorExpressionDescription([])),
}


def _mk_reference(name: str) -> Expr:
    return RefExpr(name)


GRAMMAR_WITH_ALL_COMPONENTS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=_mk_reference,
    simple_expressions=SIMPLE_EXPRESSIONS,
    complex_expressions={
        COMPLEX_A:
            grammar.ComplexExpression(ComplexA,
                                      ConstantOperatorExpressionDescription([],
                                                                            [CROSS_REF_ID])),
        COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME:
            grammar.ComplexExpression(ComplexB,
                                      ConstantOperatorExpressionDescription([],
                                                                            [CROSS_REF_ID])),
    },
    prefix_expressions=PREFIX_EXPRESSIONS,
)

GRAMMAR_SANS_COMPLEX_EXPRESSIONS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=_mk_reference,
    simple_expressions=SIMPLE_EXPRESSIONS,
    prefix_expressions=PREFIX_EXPRESSIONS,
    complex_expressions={},
)
