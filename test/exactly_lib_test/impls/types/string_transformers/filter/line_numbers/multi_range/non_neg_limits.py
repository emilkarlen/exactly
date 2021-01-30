"""
Test cases

* Positive number

 1      n (n+1)
|*--*---*|*---
| actual |
"""
import unittest
from typing import List

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.multi_range import test_resources as tr
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.multi_range.test_resources import Case
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources import \
    argument_building as range_args
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources.expectations import \
    IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources.ranges import single, from_, \
    to_, from_to
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringIntConstantSymbolContext, \
    StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestModelWNumLines0),
        unittest.makeSuite(TestModelWNumLines1),
        unittest.makeSuite(TestModelWNumLines10),
        unittest.makeSuite(TestModelWNumLines20),
        TestSymbolReferences(),
        TestIntIsPyExprAndSourceConsumption(),
    ])


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = ['1\n', '2\n', '3\n']
        single_range_1_symbol = StringIntConstantSymbolContext(
            'RANGE_SYMBOL_1',
            1,
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        single_range_2_symbol = StringIntConstantSymbolContext(
            'RANGE_SYMBOL_2',
            3,
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        symbols = [single_range_1_symbol, single_range_2_symbol]

        expected_output_lines = [input_lines[single_range_1_symbol.int_value - 1],
                                 input_lines[single_range_2_symbol.int_value - 1]]

        arguments = args.filter_line_nums__multi([
            range_args.SingleLineRange(single_range_1_symbol.name__sym_ref_syntax),
            range_args.SingleLineRange(single_range_2_symbol.name__sym_ref_syntax),
        ])
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            integration_check.expectation_of_successful_execution_2(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


class TestIntIsPyExprAndSourceConsumption(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = ['1\n', '2\n', '3\n']
        single_range_1_symbol = StringConstantSymbolContext(
            'RANGE_SYMBOL_1',
            ':1+10-10',
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        single_range_2_symbol = StringConstantSymbolContext(
            'RANGE_SYMBOL_2',
            '10-7:',
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        symbols = [single_range_1_symbol, single_range_2_symbol]

        expected_output_lines = [input_lines[1 - 1],
                                 input_lines[3 - 1]]

        arguments = args.filter_line_nums__multi([
            range_args.SingleLineRange(single_range_1_symbol.name__sym_ref_syntax),
            range_args.SingleLineRange(single_range_2_symbol.name__sym_ref_syntax),
        ])
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            integration_check.expectation_of_successful_execution_2(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


CASES__HEAD = [
    Case.w_upper_limit(
        'two head, max=1',
        [to_(1), to_(1)],
        lines_in_ranges__increasing=
        [1]
    ),
    Case.w_upper_limit(
        'two head, max=5',
        [to_(4), to_(5)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5]
    ),
    Case.w_upper_limit(
        'two head, max=9',
        [to_(4), to_(9)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
    ),
    Case.w_upper_limit(
        'two head, max=10',
        [to_(4), to_(10)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ),
    Case.w_upper_limit(
        'two head, max=11',
        [to_(4), to_(11)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ),
    Case.w_upper_limit(
        'two head, max=12',
        [to_(4), to_(12)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    ),
]

CASES__TAIL = [
    Case.wo_upper_limit(
        'two tail, min=1',
        [from_(1), from_(1)],
        lines_in_ranges__increasing=
        [1]
    ),
    Case.wo_upper_limit(
        'two tail, min=4',
        [from_(4), from_(5)],
        lines_in_ranges__increasing=
        [4]
    ),
    Case.wo_upper_limit(
        'two tail, min=9',
        [from_(13), from_(9)],
        lines_in_ranges__increasing=
        [9]
    ),
    Case.wo_upper_limit(
        'two tail, min=10',
        [from_(15), from_(10)],
        lines_in_ranges__increasing=
        [10]
    ),
    Case.wo_upper_limit(
        'two tail, min=11',
        [from_(13), from_(11)],
        lines_in_ranges__increasing=
        [11]
    ),
    Case.wo_upper_limit(
        'two tail, min=12',
        [from_(17), from_(12)],
        lines_in_ranges__increasing=
        [12]
    ),
]

CASES__BODY = [
    Case.w_upper_limit(
        'empty',
        [from_to(5, 4)],
        lines_in_ranges__increasing=
        []
    ),
    Case.w_upper_limit(
        '1st',
        [from_to(0, 1)],
        lines_in_ranges__increasing=
        [1]
    ),
    Case.w_upper_limit(
        'no borders (merged)',
        [from_to(3, 5), from_to(6, 7)],
        lines_in_ranges__increasing=
        [3, 4, 5, 6, 7]
    ),
    Case.w_upper_limit(
        'no borders (not merged)',
        [from_to(3, 5), from_to(7, 8)],
        lines_in_ranges__increasing=
        [3, 4, 5, 7, 8]
    ),
    Case.w_upper_limit(
        'borders 1,2, 10 (not merged)',
        [from_to(1, 2), from_to(8, 10)],
        lines_in_ranges__increasing=
        [1, 2, 8, 9, 10]
    ),
    Case.w_upper_limit(
        'borders 10, 11 (merged)',
        [single(10), single(11)],
        lines_in_ranges__increasing=
        [10, 11]
    ),
    Case.w_upper_limit(
        'borders 10, 11 (not merged, w segment before)',
        [single(5), from_to(10, 11)],
        lines_in_ranges__increasing=
        [5, 10, 11]
    ),
    Case.w_upper_limit(
        'borders 10, 11 (not merged, w segment after)',
        [from_to(10, 11), single(15)],
        lines_in_ranges__increasing=
        [10, 11, 15]
    ),
    Case.w_upper_limit(
        'borders 10, 11 (not merged, w segment before and after)',
        [single(5), from_to(10, 11), single(15)],
        lines_in_ranges__increasing=
        [5, 10, 11, 15]
    ),
]

CASES__HEAD_TAIL = [
    Case.wo_upper_limit(
        'everything',
        [to_(7), from_(8)],
        lines_in_ranges__increasing=
        [1]
    ),
    Case.wo_upper_limit(
        'to border, from middle',
        [to_(1), from_(3)],
        lines_in_ranges__increasing=
        [1, 3]
    ),
    Case.wo_upper_limit(
        'to middle, from border',
        [to_(3), from_(10)],
        lines_in_ranges__increasing=
        [1, 2, 3, 10]
    ),
    Case.wo_upper_limit(
        'to middle, from middle, minimum distance not merged',
        [to_(6), from_(8)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 8, 9]
    ),
    Case.wo_upper_limit(
        'to border, from <non-existing> (for 10 elements)',
        [to_(10), from_(12)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
    ),
    Case.wo_upper_limit(
        'to <non-existing>, from <non-existing> (for 10 elements)',
        [to_(11), from_(15)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15]
    ),
    Case.wo_upper_limit(
        'to <non-existing>, from <non-existing> (for 10 elements) - reversed',
        [from_(15), to_(11)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15]
    ),
    Case.wo_upper_limit(
        'multiple',
        [from_(15), to_(2), to_(4), from_(17)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 15]
    ),
]

CASES__HEAD_BODY = [
    Case.w_upper_limit(
        'to border, middle',
        [to_(1), from_to(3, 5)],
        lines_in_ranges__increasing=
        [1, 3, 4, 5]
    ),
    Case.w_upper_limit(
        'minimum distance for non-merge',
        [to_(3), from_to(5, 6)],
        lines_in_ranges__increasing=
        [1, 2, 3, 5, 6]
    ),
    Case.w_upper_limit(
        'minimum distance for non-merge (reversed)',
        [from_to(5, 6), to_(3)],
        lines_in_ranges__increasing=
        [1, 2, 3, 5, 6]
    ),
    Case.w_upper_limit(
        'to middle, border',
        [to_(3), from_to(7, 10)],
        lines_in_ranges__increasing=
        [1, 2, 3, 7, 8, 9, 10]
    ),
    Case.w_upper_limit(
        'to middle, from-<inside>to-<non-existing> (for 10 elements)',
        [to_(3), from_to(8, 11)],
        lines_in_ranges__increasing=
        [1, 2, 3, 8, 9, 10, 11]
    ),
    Case.w_upper_limit(
        'to border, from-<last>-to-<non-existing> (for 10 elements)',
        [to_(2), from_to(10, 12)],
        lines_in_ranges__increasing=
        [1, 2, 10, 11, 12]
    ),
    Case.w_upper_limit(
        'merge/overlapping',
        [to_(4), from_to(3, 5)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5]
    ),
    Case.w_upper_limit(
        'merge/overlapping (reversed)',
        [from_to(3, 5), to_(4)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5]
    ),
    Case.w_upper_limit(
        'multiple',
        [from_to(9, 10), from_to(3, 5), to_(4), to_(7), from_to(13, 15)],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 5, 6, 7, 9, 10, 13, 14, 15]
    ),
]

CASES__TAIL_BODY = [
    Case.wo_upper_limit(
        'from middle, middle',
        [from_(9), from_to(3, 5)],
        lines_in_ranges__increasing=
        [3, 4, 5, 9]
    ),
    Case.wo_upper_limit(
        'from middle, middle - min non-merge distance',
        [from_(7), from_to(3, 5)],
        lines_in_ranges__increasing=
        [3, 4, 5, 7]
    ),
    Case.wo_upper_limit(
        'from middle, middle/single - min non-merge distance',
        [from_(7), single(5)],
        lines_in_ranges__increasing=
        [5, 7]
    ),
    Case.wo_upper_limit(
        'after <non-existing>, border (for 10 elements)',
        [from_(12), from_to(9, 10)],
        lines_in_ranges__increasing=
        [9, 10, 12]
    ),

    Case.wo_upper_limit(
        'after <non-existing>, covering-border (for 10 elements)',
        [from_(13), from_to(9, 11)],
        lines_in_ranges__increasing=
        [9, 10, 11, 13]
    ),

    Case.wo_upper_limit(
        'merge',
        [from_(13), from_to(13, 17), from_to(11, 12), from_(11)],
        lines_in_ranges__increasing=
        [11, 12, 13]
    ),

    Case.wo_upper_limit(
        'multiple',
        [from_to(9, 10), from_to(3, 5), from_(15), single(13)],
        lines_in_ranges__increasing=
        [3, 4, 5, 9, 10, 13, 15]
    ),
]

CASES__HEAD_TAIL_BODY = [
    Case.wo_upper_limit(
        'middle',
        [to_(2), from_(7), from_to(4, 5)],
        lines_in_ranges__increasing=
        [1, 2, 4, 5, 7]
    ),
    Case.wo_upper_limit(
        'multiple body',
        [to_(2), from_(10), from_to(4, 5), from_to(7, 8)],
        lines_in_ranges__increasing=
        [1, 2, 4, 5, 7, 8, 10]
    ),
    Case.wo_upper_limit(
        'merge',
        [to_(2), to_(4), from_to(3, 4), single(2),
         from_to(7, 9), from_to(8, 10),
         single(12),
         from_to(14, 17), from_(16), from_(16), from_(15),
         ],
        lines_in_ranges__increasing=
        [1, 2, 3, 4, 7, 8, 9, 10, 12, 14]
    ),
]

CASES = (
        CASES__HEAD + CASES__TAIL + CASES__BODY +
        CASES__HEAD_TAIL + CASES__HEAD_BODY + CASES__TAIL_BODY +
        CASES__HEAD_TAIL_BODY
)


class TestCaseWCheckerOfConstInputBase(unittest.TestCase):
    def input(self) -> List[str]:
        raise NotImplementedError('abstract method')

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        raise NotImplementedError('abstract method')

    @property
    def checker(self) -> tr.CheckerOfConstInput:
        return tr.CheckerOfConstInput(
            self,
            self.input(),
            self.max_as_lines_invocations__when_only_checking_via_as_lines()
        )


class TestModelWNumLines0(TestCaseWCheckerOfConstInputBase):
    def input(self) -> List[str]:
        return []

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        return 1

    def test_with_model_access__only_as_lines_is_used(self):
        self.checker.check__wo_max_lines_from_iter__cases(CASES)

    def test_with_model_access__check_all_model_properties(self):
        self.checker.check__w_access_of_all_model_properties__cases(CASES)


class TestModelWNumLines1(TestCaseWCheckerOfConstInputBase):
    def input(self) -> List[str]:
        return ['1st']

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        return 1

    def test_with_model_access__only_as_lines_is_used(self):
        self.checker.check__wo_max_lines_from_iter__cases(CASES)

    def test_with_model_access__check_all_model_properties(self):
        self.checker.check__w_access_of_all_model_properties__cases(CASES)


class TestModelWNumLines10(TestCaseWCheckerOfConstInputBase):
    def input(self) -> List[str]:
        return [
            '{}\n'.format(n + 1)
            for n in range(10)
        ]

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        return 1

    def test_only_as_lines_is_used_w_limited_num_lines_accessed(self):
        self.checker.check__w_max_lines_from_iter__cases(CASES)

    def test_check_all_model_properties(self):
        self.checker.check__w_access_of_all_model_properties__cases(CASES)


class TestModelWNumLines20(TestCaseWCheckerOfConstInputBase):
    def input(self) -> List[str]:
        return [
            '{}\n'.format(n + 1)
            for n in range(20)
        ]

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        return 1

    def test_only_as_lines_is_used_w_limited_num_lines_accessed(self):
        self.checker.check__w_max_lines_from_iter__cases(CASES)

    def test_check_all_model_properties(self):
        self.checker.check__w_access_of_all_model_properties__cases(CASES)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
