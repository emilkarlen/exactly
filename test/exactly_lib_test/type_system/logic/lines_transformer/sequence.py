import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer, IdentityLinesTransformer, \
    SequenceLinesTransformer
from exactly_lib.type_system.logic.lines_transformer_values import StringTransformerSequenceValue, \
    DirDependentStringTransformerValue
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    matches_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import \
    MultiDirDependentValueTestImpl
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.line_transformers import \
    MyNonIdentityTransformer, MyToUppercaseTransformer, MyCountNumUppercaseCharactersTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPrimitiveValue),
        unittest.makeSuite(TestValue),
    ])


def equals_lines_transformer(expected: LinesTransformer) -> asrt.ValueAssertion[LinesTransformer]:
    if isinstance(expected, IdentityLinesTransformer):
        return asrt.is_instance(IdentityLinesTransformer)
    if isinstance(expected, SequenceLinesTransformer):
        return equals_sequence_transformer(expected)
    raise TypeError('Unknown type of lines transformer: ' + str(expected))


def equals_sequence_transformer(expected: SequenceLinesTransformer) -> asrt.ValueAssertion[LinesTransformer]:
    return asrt.is_instance_with(
        SequenceLinesTransformer,
        asrt.sub_component('transformers',
                           SequenceLinesTransformer.transformers.fget,
                           asrt.matches_sequence([
                               equals_lines_transformer(lt) for lt in expected.transformers
                           ])
                           )
    )


class TestValue(unittest.TestCase):
    def test_dir_dep_properties(self):
        cases = [
            NEA('no components',
                MultiDirDependentValueTestImpl(set(),
                                               SequenceLinesTransformer([])),
                StringTransformerSequenceValue([])
                ),
            NEA('single component',
                MultiDirDependentValueTestImpl({DirectoryStructurePartition.HOME},
                                               SequenceLinesTransformer([IdentityLinesTransformer()])),
                StringTransformerSequenceValue([DirDependentStringTransformerValue({DirectoryStructurePartition.HOME},
                                                                                   make_identity_transformer)])
                ),
            NEA('multiple components',
                MultiDirDependentValueTestImpl({DirectoryStructurePartition.HOME,
                                                DirectoryStructurePartition.NON_HOME},
                                               SequenceLinesTransformer([IdentityLinesTransformer(),
                                                                         IdentityLinesTransformer()])),
                StringTransformerSequenceValue([
                    DirDependentStringTransformerValue({DirectoryStructurePartition.HOME},
                                                       make_identity_transformer),
                    DirDependentStringTransformerValue({DirectoryStructurePartition.NON_HOME},
                                                       make_identity_transformer),
                ])
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = matches_multi_dir_dependent_value(case.expected, equals_lines_transformer)

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
