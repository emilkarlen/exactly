from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as expression_parser
from exactly_lib.test_case_utils.expression.grammar import OperatorExpressionDescription
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name import NameWithGenderWithFormatting, NameWithGender
from exactly_lib.util.name_and_value import NameAndValue
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


def parse_recursive_primitive_of_grammar_w_all_components(parser: TokenParser) -> PrimitiveRecursive:
    argument = expression_parser.parse(GRAMMAR_WITH_ALL_COMPONENTS,
                                       parser,
                                       must_be_on_current_line=False)
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

CONCEPT = grammar.Concept(
    NameWithGenderWithFormatting(
        NameWithGender('a',
                       'concept singular',
                       'concept plural')),
    'type-system-name',
    a.Named('SYNTAX-ELEMENT-NAME'))


class ConstantPrimitiveExprDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self,
                 argument_usage_list: Sequence[a.ArgumentUsage],
                 description_rest: Sequence[ParagraphItem],
                 syntax_elements: Sequence[SyntaxElementDescription] = (),
                 see_also_targets: Sequence[SeeAlsoTarget] = (),
                 ):
        self._argument_usage_list = argument_usage_list
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)
        self._syntax_elements = syntax_elements

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._argument_usage_list

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._syntax_elements

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


class ConstantOperatorExpressionDescription(OperatorExpressionDescription):
    def __init__(self,
                 description_rest: Sequence[ParagraphItem],
                 syntax_elements: Sequence[SyntaxElementDescription] = (),
                 see_also_targets: Sequence[SeeAlsoTarget] = (),
                 ):
        self._description_rest = description_rest
        self._see_also_targets = list(see_also_targets)
        self._syntax_elements = syntax_elements

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._description_rest

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._syntax_elements

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return self._see_also_targets


PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE = (
    NameAndValue(
        PRIMITIVE_WITH_ARG,
        grammar.PrimitiveExpression(parse_primitive_with_arg,
                                    ConstantPrimitiveExprDescription([], [],
                                                                     [SyntaxElementDescription(
                                                                         PRIMITIVE_WITH_ARG + '-SED',
                                                                         ())],
                                                                     [CROSS_REF_ID]))
    ),
    NameAndValue(
        PRIMITIVE_SANS_ARG,
        grammar.PrimitiveExpression(parse_primitive_sans_arg,
                                    ConstantPrimitiveExprDescription([], []))
    ),
)

PRIMITIVE_EXPRESSIONS__INCLUDING_RECURSIVE = (
        list(PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE) +
        [
            NameAndValue(
                PRIMITIVE_RECURSIVE,
                grammar.PrimitiveExpression(
                    parse_recursive_primitive_of_grammar_w_all_components,
                    ConstantPrimitiveExprDescription([], [])
                )
            )
        ]
)

PREFIX_OP_EXPRESSIONS = (
    NameAndValue(
        PREFIX_P,
        grammar.PrefixOpExpression(PrefixOpExprP,
                                   ConstantOperatorExpressionDescription([]))
    ),
    NameAndValue(
        PREFIX_Q,
        grammar.PrefixOpExpression(PrefixOpExprQ,
                                   ConstantOperatorExpressionDescription([]))
    ),
)


def _mk_reference(name: str) -> Expr:
    return RefExpr(name)


GRAMMAR_WITH_ALL_COMPONENTS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=_mk_reference,
    primitive_expressions=PRIMITIVE_EXPRESSIONS__INCLUDING_RECURSIVE,
    infix_op_expressions=(
        NameAndValue(
            INFIX_OP_A,
            grammar.InfixOpExpression(InfixOpA,
                                      ConstantOperatorExpressionDescription([], [],
                                                                            [CROSS_REF_ID]))
        ),
        NameAndValue(
            INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            grammar.InfixOpExpression(InfixOpB,
                                      ConstantOperatorExpressionDescription([], [],
                                                                            [CROSS_REF_ID]))
        ),
    ),
    prefix_op_expressions=PREFIX_OP_EXPRESSIONS,
)

GRAMMAR_SANS_INFIX_OP_EXPRESSIONS = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=_mk_reference,
    primitive_expressions=PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE,
    prefix_op_expressions=PREFIX_OP_EXPRESSIONS,
    infix_op_expressions=(),
)
