from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.impls.types.expression import grammar
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.name import NameWithGenderWithFormatting, NameWithGender
from exactly_lib_test.impls.types.expression.test_resources.descriptions import ConstantPrimitiveDescription, \
    ConstantOperatorDescription, ConstantInfixOperatorDescription


class Expr:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class Reference(Expr):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.symbol_name)


class Primitive(Expr):
    def __init__(self, argument: str):
        self.argument = argument

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               repr(self.argument))


class PrefixOp(Expr):
    def __init__(self, operand: Expr):
        self.operand = operand

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                               str(self.operand))


class InfixOpExpr(Expr):
    def __init__(self, operands: Sequence[Expr]):
        self.operands = operands

    def __str__(self):
        return '{}[{}]'.format(self.__class__.__name__,
                               ', '.join(map(str, self.operands)))


class InfixOp1u(InfixOpExpr):
    pass


class InfixOp1v(InfixOpExpr):
    pass


class InfixOp2u(InfixOpExpr):
    pass


class InfixOp2v(InfixOpExpr):
    pass


def parse_primitive(parser: TokenParser) -> Primitive:
    token = parser.consume_mandatory_token('failed parse of simple expression with arg')
    return Primitive(token.string)


CROSS_REF_ID = CustomCrossReferenceId('custom-target')

PRIMITIVE_WITH_ARG = 'primitive'

POP = 'prefix_op'

NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME = 'not/a/primitive/expr/name/and/not/a/valid/symbol/name'

IOP_1u = 'infix_op_1u'
IOP_1v = 'infix_op_1v'
IOP_2u = 'infix_op_2u'
IOP_2v = 'infix_op_2v'

CONCEPT = grammar.Concept(
    NameWithGenderWithFormatting(
        NameWithGender('a',
                       'concept singular',
                       'concept plural')),
    'type-system-name',
    a.Named('SYNTAX-ELEMENT-NAME'))

INFIX_OPERATOR_DESCRIPTION = ConstantInfixOperatorDescription([], [], [CROSS_REF_ID])


def _mk_reference(name: str) -> Expr:
    return Reference(name)


GRAMMAR = grammar.Grammar(
    concept=CONCEPT,
    mk_reference=_mk_reference,
    primitives=(
        NameAndValue(
            PRIMITIVE_WITH_ARG,
            grammar.Primitive(
                parse_primitive,
                ConstantPrimitiveDescription([], [],
                                             [SyntaxElementDescription(
                                                 PRIMITIVE_WITH_ARG + '-SED',
                                                 ())],
                                             [CROSS_REF_ID]))
        ),
    ),
    prefix_operators=[
        NameAndValue(
            POP,
            grammar.PrefixOperator(PrefixOp,
                                   ConstantOperatorDescription([]))
        ),
    ],
    infix_operators_in_order_of_increasing_precedence=[
        [
            NameAndValue(
                IOP_2u,
                grammar.InfixOperator(InfixOp2u, INFIX_OPERATOR_DESCRIPTION)
            ),
            NameAndValue(
                IOP_2v,
                grammar.InfixOperator(InfixOp2v, INFIX_OPERATOR_DESCRIPTION)
            ),
        ],
        [
            NameAndValue(
                IOP_1u,
                grammar.InfixOperator(InfixOp1u, INFIX_OPERATOR_DESCRIPTION)
            ),
            NameAndValue(
                IOP_1v,
                grammar.InfixOperator(InfixOp1v, INFIX_OPERATOR_DESCRIPTION)
            ),
        ],
    ],
)
