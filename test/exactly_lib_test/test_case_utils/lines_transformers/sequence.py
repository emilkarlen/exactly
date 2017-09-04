import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer, \
    SequenceLinesTransformer
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_transformers_list(self):
        # ARRANGE #
        t_1 = IdentityLinesTransformer()
        t_2 = IdentityLinesTransformer()
        transformers_given_to_constructor = [t_1, t_2]

        # ACT #

        sequence = SequenceLinesTransformer(transformers_given_to_constructor)
        transformers_from_sequence = sequence.transformers

        # ASSERT #

        self.assertEqual(transformers_given_to_constructor,
                         list(transformers_from_sequence))

    def test_WHEN_sequence_of_transformers_is_empty_THEN_output_SHOULD_be_equal_to_input(self):
        # ARRANGE #
        tcds = fake_home_and_sds()
        sequence = SequenceLinesTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        input_iter = iter(input_lines)
        # ACT #
        output = sequence.transform(tcds, input_iter)
        # ASSERT #
        output_lines = list(output)

        self.assertEqual(input_lines,
                         output_lines)

    def test_WHEN_single_transformer_THEN_sequence_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        tcds = fake_home_and_sds()

        to_upper_t = MyToUppercaseTransformer()

        sequence = SequenceLinesTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']

        # ACT #

        actual = sequence.transform(tcds, iter(input_lines))

        # ASSERT #

        expected_output_lines = ['FIRST',
                                 'SECOND',
                                 'THIRD']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)

    def test_WHEN_multiple_transformers_THEN_transformers_SHOULD_be_chained(self):
        # ARRANGE #

        tcds = fake_home_and_sds()

        to_upper_t = MyToUppercaseTransformer()
        count_num_upper = MyCountNumUppercaseCharactersTransformer()

        sequence = SequenceLinesTransformer([to_upper_t,
                                             count_num_upper])

        input_lines = ['this is',
                       'the',
                       'input']

        # ACT #

        actual = sequence.transform(tcds, iter(input_lines))

        # ASSERT #

        expected_output_lines = ['6',
                                 '3',
                                 '5']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)


class MyToUppercaseTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        return map(str.upper, lines)


class MyCountNumUppercaseCharactersTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        return map(get_number_of_uppercase_characters, lines)


def get_number_of_uppercase_characters(line: str) -> str:
    ret_val = 0
    for ch in line:
        if ch.isupper():
            ret_val += 1
    return str(ret_val)
