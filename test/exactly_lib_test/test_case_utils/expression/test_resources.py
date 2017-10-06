from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.help_texts.cross_reference_id import CustomCrossReferenceId
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.expression import grammar
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
    def __init__(self, expressions: list):
        self.expressions = expressions

    def __str__(self):
        return '{}[{}]'.format(self.__class__.__name__,
                               ', '.join(map(str, self.expressions)))


class ComplexA(ComplexExpr):
    pass


class ComplexB(ComplexExpr):
    pass


def parse_simple_with_arg(parser: TokenParserPrime) -> SimpleWithArg:
    token = parser.consume_mandatory_token('failed parse of simple expression with arg')
    return SimpleWithArg(token.string)


def parse_simple_sans_arg(parser: TokenParserPrime) -> SimpleSansArg:
    return SimpleSansArg()


CROSS_REF_ID = CustomCrossReferenceId('custom-target')

SIMPLE_WITH_ARG = 'simple_with_arg'
SIMPLE_SANS_ARG = 'simple_sans_arg'

NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME = 'not/a/simple/expr/name/and/not/a/valid/symbol/name'

PREFIX_P = '!'
PREFIX_Q = 'prefix_q'

COMPLEX_A = 'complex_a'
COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME = '||'

CONCEPT = grammar.Concept(grammar.Name('concept singular',
                                       'concept plural'),
                          'type-system-name',
                          a.Named('SYNTAX-ELEMENT-NAME'))

SIMPLE_EXPRESSIONS = {
    SIMPLE_WITH_ARG: grammar.SimpleExpression(parse_simple_with_arg,
                                              grammar.SimpleExpressionDescription([], [],
                                                                                  SeeAlsoSet([CROSS_REF_ID]))),
    SIMPLE_SANS_ARG: grammar.SimpleExpression(parse_simple_sans_arg,
                                              grammar.SimpleExpressionDescription([], [])),
}

PREFIX_EXPRESSIONS = {
    PREFIX_P: grammar.PrefixExpression(PrefixExprP,
                                       grammar.OperatorExpressionDescription([])),
    PREFIX_Q: grammar.PrefixExpression(PrefixExprQ,
                                       grammar.OperatorExpressionDescription([])),
}

GRAMMAR_WITH_ALL_COMPONENTS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=RefExpr,
    simple_expressions=SIMPLE_EXPRESSIONS,
    complex_expressions={
        COMPLEX_A:
            grammar.ComplexExpression(ComplexA,
                                      grammar.OperatorExpressionDescription([],
                                                                            SeeAlsoSet([CROSS_REF_ID]))),
        COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME:
            grammar.ComplexExpression(ComplexB,
                                      grammar.OperatorExpressionDescription([],
                                                                            SeeAlsoSet([CROSS_REF_ID]))),
    },
    prefix_expressions=PREFIX_EXPRESSIONS,
)

GRAMMAR_SANS_COMPLEX_EXPRESSIONS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=RefExpr,
    simple_expressions=SIMPLE_EXPRESSIONS,
    prefix_expressions=PREFIX_EXPRESSIONS,
    complex_expressions={},
)
