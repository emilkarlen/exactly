import unittest
from typing import List

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.expression.test_resources.infix_op_precedence_grammar import PRIMITIVE_WITH_ARG, \
    Primitive, POP, PrefixOp, Reference, IOP_1u, InfixOp1u, IOP_2u, InfixOp2u, IOP_1v, InfixOp1v, \
    InfixOp2v, IOP_2v
from exactly_lib_test.impls.types.expression.test_resources.parse_check_w_precedence import \
    check__simple_and_full__multi, check__full_and_simple_within_parenthesis__multi
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestWoInfixOperators(),
        TestSingleInfixOperator(),
        TestMultipleInfixOperatorsWithSamePrecedence(),
        TestInfixOperatorsWithDifferentPrecedences(),
    ])


class TestWoInfixOperators(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE('just simple',
                input_value=_src_of([Pa.name]),
                expected_value=Pa.value,
                ),
            NIE('prefix op of simple',
                input_value=_src_of([POP, Pa.name]),
                expected_value=PrefixOp(Pa.value),
                ),
            NIE('reference',
                input_value=_src_of([REF.name]),
                expected_value=REF.value,
                ),
        ]
        # ACT & ASSERT #
        check__simple_and_full__multi(
            self,
            cases,
        )


class TestSingleInfixOperator(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE('infix op of precedence 1',
                input_value=_src_of([Pa.name, IOP_1u, Pb.name]),
                expected_value=InfixOp1u([Pa.value, Pb.value]),
                ),
            NIE('infix op of precedence 1, and prefix operator',
                input_value=_src_of([POP, Pa.name, IOP_1u, POP, Pb.name]),
                expected_value=InfixOp1u([PrefixOp(Pa.value), PrefixOp(Pb.value)]),
                ),
            NIE('infix op of precedence 2',
                input_value=_src_of([Pa.name, IOP_2u, Pb.name]),
                expected_value=InfixOp2u([Pa.value, Pb.value]),
                ),
            NIE('infix op of precedence 2, and prefix operator',
                input_value=_src_of([POP, Pa.name, IOP_2u, POP, Pb.name]),
                expected_value=InfixOp2u([PrefixOp(Pa.value), PrefixOp(Pb.value)]),
                ),
        ]
        # ACT & ASSERT #
        check__full_and_simple_within_parenthesis__multi(
            self,
            cases,
        )


class TestMultipleInfixOperatorsWithSamePrecedence(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE('infix op of precedence 1',
                input_value=_src_of([Pa.name, IOP_1u, Pb.name, IOP_1v, Pc.name]),
                expected_value=InfixOp1v([
                    InfixOp1u([Pa.value, Pb.value]),
                    Pc.value,
                ]),
                ),
            NIE('infix op of precedence 1, and prefix operator',
                input_value=_src_of([POP, Pa.name, IOP_1u, POP, Pb.name, IOP_1v, POP, Pc.name]),
                expected_value=InfixOp1v([
                    InfixOp1u([PrefixOp(Pa.value), PrefixOp(Pb.value)]),
                    PrefixOp(Pc.value),
                ]),
                ),
            NIE('infix op of precedence 2',
                input_value=_src_of([Pa.name, IOP_2u, Pb.name, IOP_2v, Pc.name]),
                expected_value=InfixOp2v([
                    InfixOp2u([Pa.value, Pb.value]),
                    Pc.value,
                ]),
                ),
            NIE('infix op of precedence 2, and prefix operator',
                input_value=_src_of([POP, Pa.name, IOP_2u, POP, Pb.name, IOP_2v, POP, Pc.name]),
                expected_value=InfixOp2v([
                    InfixOp2u([PrefixOp(Pa.value), PrefixOp(Pb.value)]),
                    PrefixOp(Pc.value),
                ]),
                ),
        ]
        # ACT & ASSERT #
        check__full_and_simple_within_parenthesis__multi(
            self,
            cases,
        )


class TestInfixOperatorsWithDifferentPrecedences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE('single infix op of every precedence / highest first',
                input_value=_src_of([Pa.name, IOP_1u, Pb.name, IOP_2u, Pc.name]),
                expected_value=InfixOp2u([
                    InfixOp1u([Pa.value, Pb.value]),
                    Pc.value,
                ]),
                ),
            NIE('single infix op of every precedence / lowest first',
                input_value=_src_of([Pa.name,
                                     IOP_2u,
                                     Pb.name, IOP_1u, Pc.name]),
                expected_value=InfixOp2u([
                    Pa.value,
                    InfixOp1u([Pb.value, Pc.value]),
                ]),
                ),

            NIE('infix op of lowest, surrounded by infix-op-expr of higher on each side',
                input_value=_src_of([Pa.name, IOP_1u, Pb.name,
                                     IOP_2u,
                                     Pc.name, IOP_1u, Pd.name]),
                expected_value=InfixOp2u([
                    InfixOp1u([Pa.value, Pb.value]),
                    InfixOp1u([Pc.value, Pd.value]),
                ]),
                ),
            NIE('2 infix-op of lowest, with 3 arguments: simple, infix-op-highest-expr, simple',
                input_value=_src_of([Pa.name,
                                     IOP_2u,
                                     Pb.name, IOP_1u, Pc.name,
                                     IOP_2u,
                                     Pd.name]),
                expected_value=InfixOp2u([
                    Pa.value,
                    InfixOp1u([Pb.value, Pc.value]),
                    Pd.value,
                ]),
                ),
            NIE('',
                input_value=_src_of([Pa.name, IOP_1u, Pb.name,
                                     IOP_2u,
                                     Pc.name, IOP_1v, Pd.name,
                                     IOP_1u,
                                     Pe.name]),
                expected_value=InfixOp2u([
                    InfixOp1u([Pa.value, Pb.value]),
                    InfixOp1u([InfixOp1v([Pc.value, Pd.value]),
                               Pe.value]),
                ]),
                ),
        ]
        # ACT & ASSERT #
        check__full_and_simple_within_parenthesis__multi(
            self,
            cases,
        )


def _prim(arg: str) -> NameAndValue[Primitive]:
    return NameAndValue(PRIMITIVE_WITH_ARG + ' ' + arg,
                        Primitive(arg))


Pa = _prim('A')
Pb = _prim('B')
Pc = _prim('C')
Pd = _prim('D')
Pe = _prim('E')

REF = NameAndValue('reference', Reference('reference'))


def _src_of(expressions: List[str]) -> str:
    return ' '.join(expressions)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
