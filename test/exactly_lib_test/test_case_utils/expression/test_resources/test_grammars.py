from typing import Sequence, Callable

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as expression_parser
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.expression.test_resources.descriptions import ConstantPrimitiveDescription, \
    ConstantOperatorDescription, CONCEPT


class Expr:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return True

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class RefExpr(Expr):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.symbol_name)


class PrefixOpExprBase(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               str(self.expression))


class PrefixOpExprP(PrefixOpExprBase):
    pass


class PrefixOpExprQ(PrefixOpExprBase):
    pass


class PrimitiveExpr(Expr):
    pass


class PrimitiveWithArg(PrimitiveExpr):
    def __init__(self, argument: str):
        self.argument = argument

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               repr(self.argument))


class PrimitiveSansArg(PrimitiveExpr):
    def __str__(self):
        return self.__class__.__name__


class PrimitiveRecursive(PrimitiveExpr):
    def __init__(self, argument: Expr):
        self.argument = argument

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               str(self.argument))


class InfixOpExpr(Expr):
    def __init__(self, expressions: Sequence[Expr]):
        self.expressions = expressions

    def __str__(self):
        return '{}[{}]'.format(self.__class__.__name__,
                               ', '.join(map(str, self.expressions)))


class InfixOpA(InfixOpExpr):
    pass


class InfixOpB(InfixOpExpr):
    pass


def parse_primitive_with_arg(parser: TokenParser) -> PrimitiveWithArg:
    token = parser.consume_mandatory_token('failed parse of simple expression with arg')
    return PrimitiveWithArg(token.string)


def parse_primitive_sans_arg(parser: TokenParser) -> PrimitiveSansArg:
    return PrimitiveSansArg()


def parse_recursive_primitive_of_grammar_w_all_components(token_parser: TokenParser) -> PrimitiveRecursive:
    expr_parser = expression_parser.parsers(GRAMMAR_WITH_ALL_COMPONENTS, False).simple
    argument = expr_parser.parse_from_token_parser(token_parser)
    return PrimitiveRecursive(argument)


CROSS_REF_ID = CustomCrossReferenceId('custom-target')

PRIMITIVE_WITH_ARG = 'primitive_with_arg'
PRIMITIVE_SANS_ARG = 'primitive_sans_arg'
PRIMITIVE_RECURSIVE = 'primitive_recursive'

NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME = 'not/a/primitive/expr/name/and/not/a/valid/symbol/name'

PREFIX_P = '!'
PREFIX_Q = 'prefix_q'

INFIX_OP_A = 'infix_op_a'
INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME = '||'


def infix_op_of(name: str, mk_expr: Callable[[Sequence[Expr]], Expr]) -> NameAndValue[grammar.InfixOperator[Expr]]:
    return NameAndValue(
        name,
        grammar.InfixOperator(mk_expr,
                              ConstantOperatorDescription([], [],
                                                          [CROSS_REF_ID]))
    )


def prefix_op(name: str, mk_expr: Callable[[Expr], Expr]) -> NameAndValue[grammar.PrefixOperator[Expr]]:
    return NameAndValue(
        name,
        grammar.PrefixOperator(mk_expr,
                               ConstantOperatorDescription([]))

    )


PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE = (
    NameAndValue(
        PRIMITIVE_WITH_ARG,
        grammar.Primitive(parse_primitive_with_arg,
                          ConstantPrimitiveDescription([], [],
                                                       [SyntaxElementDescription(
                                                           PRIMITIVE_WITH_ARG + '-SED',
                                                           ())],
                                                       [CROSS_REF_ID]))
    ),
    NameAndValue(
        PRIMITIVE_SANS_ARG,
        grammar.Primitive(parse_primitive_sans_arg,
                          ConstantPrimitiveDescription([], []))
    ),
)

PRIMITIVE_EXPRESSIONS__INCLUDING_RECURSIVE = (
        list(PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE) +
        [
            NameAndValue(
                PRIMITIVE_RECURSIVE,
                grammar.Primitive(
                    parse_recursive_primitive_of_grammar_w_all_components,
                    ConstantPrimitiveDescription([], [])
                )
            )
        ]
)

PREFIX_OP_EXPRESSIONS = (
    prefix_op(PREFIX_P, PrefixOpExprP),
    prefix_op(PREFIX_Q, PrefixOpExprQ),
)


def _mk_reference(name: str) -> Expr:
    return RefExpr(name)


def grammar_of(
        primitives: Sequence[NameAndValue[grammar.Primitive[Expr]]],
        prefix_operators: Sequence[NameAndValue[grammar.PrefixOperator[Expr]]],
        infix_operators_in_order_of_increasing_precedence:
        Sequence[Sequence[NameAndValue[grammar.InfixOperator[Expr]]]],
) -> grammar.Grammar[Expr]:
    return grammar.Grammar(
        concept=CONCEPT,
        mk_reference=_mk_reference,
        primitives=primitives,
        prefix_operators=prefix_operators,
        infix_operators_in_order_of_increasing_precedence=infix_operators_in_order_of_increasing_precedence,
    )


GRAMMAR_WITH_ALL_COMPONENTS = grammar_of(
    primitives=PRIMITIVE_EXPRESSIONS__INCLUDING_RECURSIVE,
    prefix_operators=PREFIX_OP_EXPRESSIONS,
    infix_operators_in_order_of_increasing_precedence=[(
        infix_op_of(INFIX_OP_A, InfixOpA),
        infix_op_of(INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME, InfixOpB),
    )],
)

GRAMMAR_SANS_INFIX_OP_EXPRESSIONS = grammar_of(
    primitives=PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE,
    prefix_operators=PREFIX_OP_EXPRESSIONS,
    infix_operators_in_order_of_increasing_precedence=(),
)

GRAMMARS = [
    NameAndValue(
        'sans infix-op expressions',
        GRAMMAR_SANS_INFIX_OP_EXPRESSIONS,
    ),
    NameAndValue(
        'with infix-op expressions',
        GRAMMAR_WITH_ALL_COMPONENTS,
    ),
]
