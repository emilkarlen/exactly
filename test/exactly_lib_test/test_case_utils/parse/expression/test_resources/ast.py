from exactly_lib.test_case_utils.parse.expression import grammar
from exactly_lib.test_case_utils.token_stream_parse_prime import TokenParserPrime
from exactly_lib.util.cli_syntax.elements import argument as a


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


class SimpleExpr(Expr):
    pass


class SimpleWithArg(SimpleExpr):
    def __init__(self, argument: str):
        self.argument = argument


class SimpleSansArg(SimpleExpr):
    pass


class ComplexExpr(Expr):
    def __init__(self, expressions: list):
        self.expressions = expressions


class ComplexA(ComplexExpr):
    pass


class ComplexB(ComplexExpr):
    pass


def parse_simple_with_arg(parser: TokenParserPrime) -> SimpleWithArg:
    token = parser.consume_mandatory_token('err msg format')
    return SimpleWithArg(token.string)


def parse_simple_sans_arg(parser: TokenParserPrime) -> SimpleSansArg:
    return SimpleSansArg()


SIMPLE_WITH_ARG = 'simple_with_arg'
SIMPLE_SANS_ARG = 'simple_sans_arg'

NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME = 'not/a/simple/expr/name/and/not/a/valid/symbol/name'

COMPLEX_A = 'complex_a'
COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME = '||'

GRAMMAR_WITH_ALL_COMPONENTS = grammar.Grammar(
    concept=grammar.Concept(grammar.Name('concept singular',
                                         'concept plural'),
                            'type-system-name',
                            a.Named('SYNTAX-ELEMENT-NAME')),
    mk_reference=RefExpr,
    simple_expressions={
        SIMPLE_WITH_ARG: grammar.SimpleExpression(parse_simple_with_arg,
                                                  grammar.SimpleExpressionDescription([], [])),
        SIMPLE_SANS_ARG: grammar.SimpleExpression(parse_simple_sans_arg,
                                                  grammar.SimpleExpressionDescription([], [])),
    },
    complex_expressions={
        COMPLEX_A:
            grammar.ComplexExpression(ComplexA,
                                      grammar.ComplexExpressionDescription([])),
        COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME:
            grammar.ComplexExpression(ComplexB,
                                      grammar.ComplexExpressionDescription([])),
    },
)
