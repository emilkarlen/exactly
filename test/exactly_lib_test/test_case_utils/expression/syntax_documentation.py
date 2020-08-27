import unittest
from typing import Sequence

from exactly_lib.test_case_utils.expression import syntax_documentation as sut
from exactly_lib.test_case_utils.expression.grammar import InfixOperator, PrefixOperator, Grammar
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.help.test_resources.see_also_assertions import is_see_also_target_list
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import \
    is_syntax_element_description, is_invokation_variant
from exactly_lib_test.test_case_utils.expression.test_resources import test_grammars
from exactly_lib_test.test_case_utils.expression.test_resources.test_grammars import Expr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMisc),
        unittest.makeSuite(TestPrecedenceDescriptions),
    ])


class TestMisc(unittest.TestCase):
    def test_syntax_element_description(self):
        actual = sut.syntax_element_description(test_grammars.GRAMMAR_WITH_ALL_COMPONENTS)
        is_syntax_element_description.apply_without_message(self, actual)

    def test_syntax_element_descriptions(self):
        syntax = sut.Syntax(test_grammars.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.syntax_element_descriptions()
        self.assertGreater(len(actual), 0, 'number of syntax element descriptions')
        asrt.is_sequence_of(is_syntax_element_description).apply_without_message(self, actual)

    def test_syntax_descriptions(self):
        syntax = sut.Syntax(test_grammars.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.syntax_description()
        self.assertGreater(len(actual), 0, 'number of paragraphs')
        asrt.is_sequence_of(asrt_struct.is_paragraph_item).apply_without_message(self, actual)

    def test_invokation_variants(self):
        syntax = sut.Syntax(test_grammars.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.invokation_variants()
        self.assertGreater(len(actual), 0, 'number of elements')
        asrt.is_sequence_of(is_invokation_variant).apply_without_message(self, actual)

    def test_see_also_set(self):
        syntax = sut.Syntax(test_grammars.GRAMMAR_WITH_ALL_COMPONENTS)
        actual = syntax.see_also_targets()
        is_see_also_target_list.apply_without_message(self, actual)


class TestPrecedenceDescriptions(unittest.TestCase):
    def test_precedence_description_SHOULD_be_empty(self):
        cases = [
            NameAndValue(
                'grammar wo operators',
                _grammar_with_operators((), ())
            ),
            NameAndValue(
                'grammar w just single prefix op',
                _grammar_with_operators(
                    [test_grammars.prefix_op('name', test_grammars.PrefixOpExprP)],
                    (),
                )
            ),
            NameAndValue(
                'grammar w just single infix op',
                _grammar_with_operators(
                    (),
                    [[test_grammars.infix_op_of('name', test_grammars.InfixOpA)]],
                )
            ),
            NameAndValue(
                'grammar w just 2 prefix OPs',
                _grammar_with_operators(
                    [test_grammars.prefix_op('op_1', test_grammars.PrefixOpExprP),
                     test_grammars.prefix_op('op_2', test_grammars.PrefixOpExprP)],
                    (),
                )
            ),
        ]
        for case in cases:
            syntax = sut.Syntax(case.value)
            with self.subTest(case.name):
                # ACT #
                actual = syntax.precedence_description()
                # ASSERT #
                self.assertEqual(0, len(actual), 'number of paragraphs')

    def test_precedence_description_SHOULD_not_be_empty(self):
        cases = [
            NameAndValue(
                'grammar w just 2 infix OPs (of same precedence)',
                _grammar_with_operators(
                    (),
                    [[test_grammars.infix_op_of('op_1', test_grammars.InfixOpA),
                      test_grammars.infix_op_of('op_2', test_grammars.InfixOpA)]],
                )
            ),
            NameAndValue(
                'grammar w just 2 infix OPs (of different precedences)',
                _grammar_with_operators(
                    (),
                    [
                        [test_grammars.infix_op_of('op_1', test_grammars.InfixOpA)],
                        [test_grammars.infix_op_of('op_2', test_grammars.InfixOpA)],
                    ],
                )
            ),
            NameAndValue(
                'grammar w 1 prefix OP & 1 infix OP',
                _grammar_with_operators(
                    [test_grammars.prefix_op('prefix_op', test_grammars.PrefixOpExprP)],
                    [[test_grammars.infix_op_of('infix_op', test_grammars.InfixOpA)]],
                )
            ),
        ]
        for case in cases:
            syntax = sut.Syntax(case.value)
            with self.subTest(case.name):
                # ACT #
                actual = syntax.precedence_description()
                # ASSERT #
                self.assertGreater(len(actual), 0, 'number of paragraphs')
                asrt.is_sequence_of(asrt_struct.is_paragraph_item).apply_without_message(self, actual)


def _grammar_with_operators(prefix_operators: Sequence[NameAndValue[PrefixOperator[Expr]]],
                            infix_operators_in_order_of_increasing_precedence:
                            Sequence[Sequence[NameAndValue[InfixOperator[Expr]]]],
                            ) -> Grammar[Expr]:
    return test_grammars.grammar_of(
        test_grammars.PRIMITIVE_EXPRESSIONS__EXCEPT_RECURSIVE,
        prefix_operators,
        infix_operators_in_order_of_increasing_precedence,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
