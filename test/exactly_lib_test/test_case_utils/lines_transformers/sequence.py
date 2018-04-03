import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.test_case_utils.lines_transformer.values import LinesTransformerSequenceValue, \
    DirDependentLinesTransformerValue
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer, IdentityLinesTransformer, \
    SequenceLinesTransformer
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import \
    MultiDirDependentValueTestImpl
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.test_transformers import \
    MyNonIdentityTransformer, MyToUppercaseTransformer, MyCountNumUppercaseCharactersTransformer
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.value_assertions import equals_lines_transformer
from exactly_lib_test.test_resources.test_utils import NEA


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPrimitiveValue),
        unittest.makeSuite(TestValue),
    ])


class TestValue(unittest.TestCase):
    def test_dir_dep_properties(self):
        cases = [
            NEA('no components',
                MultiDirDependentValueTestImpl(set(),
                                               SequenceLinesTransformer([])),
                LinesTransformerSequenceValue([])
                ),
            NEA('single component',
                MultiDirDependentValueTestImpl({ResolvingDependency.HOME},
                                               SequenceLinesTransformer([IdentityLinesTransformer()])),
                LinesTransformerSequenceValue([DirDependentLinesTransformerValue({ResolvingDependency.HOME},
                                                                                 make_identity_transformer)])
                ),
            NEA('multiple components',
                MultiDirDependentValueTestImpl({ResolvingDependency.HOME,
                                                ResolvingDependency.NON_HOME},
                                               SequenceLinesTransformer([IdentityLinesTransformer(),
                                                                         IdentityLinesTransformer()])),
                LinesTransformerSequenceValue([
                    DirDependentLinesTransformerValue({ResolvingDependency.HOME},
                                                      make_identity_transformer),
                    DirDependentLinesTransformerValue({ResolvingDependency.NON_HOME},
                                                      make_identity_transformer),
                ])
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = equals_multi_dir_dependent_value(case.expected, equals_lines_transformer)

                assertion.apply_without_message(self, case.actual)


def make_identity_transformer(tcds: HomeAndSds) -> LinesTransformer:
    return IdentityLinesTransformer()


class TestPrimitiveValue(unittest.TestCase):
    def test_SHOULD_is_identity_transformer(self):
        cases = [
            (
                'empty list of transformers',
                SequenceLinesTransformer([]),
                True,
            ),
            (
                'single identity transformer',
                SequenceLinesTransformer([IdentityLinesTransformer()]),
                True,
            ),
            (
                'multiple identity transformers',
                SequenceLinesTransformer([IdentityLinesTransformer(),
                                          IdentityLinesTransformer()]),
                True,
            ),
            (
                'non-identity transformer',
                SequenceLinesTransformer([MyNonIdentityTransformer()]),
                False,
            ),
        ]
        for case_name, transformer, expected in cases:
            with self.subTest(case_name=case_name):
                self.assertEqual(expected,
                                 transformer.is_identity_transformer,
                                 'is_identity_transformation')

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
        sequence = SequenceLinesTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        input_iter = iter(input_lines)
        # ACT #
        output = sequence.transform(input_iter)
        # ASSERT #
        output_lines = list(output)

        self.assertEqual(input_lines,
                         output_lines)

    def test_WHEN_single_transformer_THEN_sequence_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()

        sequence = SequenceLinesTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['FIRST',
                                 'SECOND',
                                 'THIRD']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)

    def test_WHEN_multiple_transformers_THEN_transformers_SHOULD_be_chained(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()
        count_num_upper = MyCountNumUppercaseCharactersTransformer()

        sequence = SequenceLinesTransformer([to_upper_t,
                                             count_num_upper])

        input_lines = ['this is',
                       'the',
                       'input']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['6',
                                 '3',
                                 '5']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)
