import unittest
from typing import Callable, Sequence, List

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums import sources as sut, range_merge
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import SingleLineRange, Range
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.sources import \
    SegmentsWithPositiveIncreasingValues
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_source.test_resources.dir_file_space_getter import \
    dir_file_space_with_existing_dir
from exactly_lib_test.impls.types.string_transformers.test_resources import freeze_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources
from exactly_lib_test.type_val_prims.string_source.test_resources.string_sources import StringSourceMethod


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUnconditionallyEmptyTransformations),
        unittest.makeSuite(TestNonUnconditionallyEmptyTransformationsExceptMultipleRangesWNegativeValues),
        unittest.makeSuite(TestMultipleRangesWNegativeValues),
    ])


class TestUnconditionallyEmptyTransformations(unittest.TestCase):
    def test_freeze_should_not_freeze_source_model(self):
        # ARRANGE #
        with dir_file_space_with_existing_dir() as tmp_file_space:
            for may_depend_on_external_resources in [False, True]:
                for num_initial_freeze_invocations in [1, 2]:
                    with self.subTest(may_depend_on_external_resources=may_depend_on_external_resources,
                                      num_initial_freeze_invocations=num_initial_freeze_invocations):
                        # ACT & ASSERT #
                        freeze_check.check(
                            self,
                            sut.Empty,
                            may_depend_on_external_resources,
                            num_initial_freeze_invocations,
                            tmp_file_space,
                            source_model_method_invocations=asrt.is_empty_sequence,
                        )

    def test_dependence_on_external_resources_should_UNFORTUNATELY_be_that_of_source_model(self):
        # TODO ext-deps should be False - but a bit tricky to test since it is a rare exception.
        # ARRANGE #
        tmp_file_space = DirFileSpaceThatMustNoBeUsed()
        for source_may_depend_on_external_resources in [False, True]:
            with self.subTest(source_may_depend_on_external_resources=source_may_depend_on_external_resources):
                source_model = string_sources.of_string('the contents',
                                                        tmp_file_space,
                                                        source_may_depend_on_external_resources)
                # ACT #
                string_source = sut.Empty(source_model)
                # ASSERT #
                self.assertEqual(string_source.may_depend_on_external_resources,
                                 source_may_depend_on_external_resources)


class TestNonUnconditionallyEmptyTransformationsExceptMultipleRangesWNegativeValues(unittest.TestCase):
    def test_freeze_should_cache_result(self):
        # ARRANGE #
        with dir_file_space_with_existing_dir() as tmp_file_space:
            for transformer_case in _non_unconditionally_empty_transformers_except_MultipleRangesWNegativeValues():
                for may_depend_on_external_resources in [False, True]:
                    for num_initial_freeze_invocations in [1, 2]:
                        with self.subTest(transformer=transformer_case.name,
                                          may_depend_on_external_resources=may_depend_on_external_resources,
                                          num_initial_freeze_invocations=num_initial_freeze_invocations):
                            # ACT & ASSERT #
                            freeze_check.check(
                                self,
                                transformer_case.value,
                                may_depend_on_external_resources,
                                num_initial_freeze_invocations,
                                tmp_file_space,
                                source_model_method_invocations=
                                freeze_check.single_method_invocation_that_is(StringSourceMethod.AS_LINES)
                            )

    def test_dependence_on_external_resources_should_be_that_of_source_model(self):
        # ARRANGE #
        tmp_file_space = DirFileSpaceThatMustNoBeUsed()
        for transformer_case in _non_unconditionally_empty_transformers_except_MultipleRangesWNegativeValues():
            for source_may_depend_on_external_resources in [False, True]:
                with self.subTest(transformer=transformer_case.name,
                                  source_may_depend_on_external_resources=source_may_depend_on_external_resources):
                    source_model = string_sources.of_string('the contents',
                                                            tmp_file_space,
                                                            source_may_depend_on_external_resources)
                    # ACT #
                    string_source = transformer_case.value(source_model)
                    # ASSERT #
                    self.assertEqual(string_source.may_depend_on_external_resources,
                                     source_may_depend_on_external_resources)


class TestMultipleRangesWNegativeValues(unittest.TestCase):
    def test_freeze_should_cache_result(self):
        # ARRANGE #
        with dir_file_space_with_existing_dir() as tmp_file_space:
            for transformer_case in multiple_ranges_w_negative_values_cases():
                for may_depend_on_external_resources in [False, True]:
                    for num_initial_freeze_invocations in [1, 2]:
                        with self.subTest(transformer=transformer_case.name,
                                          may_depend_on_external_resources=may_depend_on_external_resources,
                                          num_initial_freeze_invocations=num_initial_freeze_invocations):
                            # ACT & ASSERT #
                            freeze_check.check(
                                self,
                                transformer_case.transformer,
                                may_depend_on_external_resources,
                                num_initial_freeze_invocations,
                                tmp_file_space,
                                source_model_method_invocations=
                                transformer_case.source_model_method_invocations,
                                source_model_contents=transformer_case.source_model_contents,
                            )

    def test_dependence_on_external_resources_should_be_that_of_source_model(self):
        # ARRANGE #
        tmp_file_space = DirFileSpaceThatMustNoBeUsed()
        for transformer_case in multiple_ranges_w_negative_values_cases():
            for source_may_depend_on_external_resources in [False, True]:
                with self.subTest(transformer=transformer_case.name,
                                  source_may_depend_on_external_resources=source_may_depend_on_external_resources):
                    source_model = string_sources.of_string('the contents',
                                                            tmp_file_space,
                                                            source_may_depend_on_external_resources)
                    # ACT #
                    string_source = transformer_case.transformer(source_model)
                    # ASSERT #
                    self.assertEqual(string_source.may_depend_on_external_resources,
                                     source_may_depend_on_external_resources)


def _non_unconditionally_empty_transformers_except_MultipleRangesWNegativeValues(
) -> Sequence[NameAndValue[Callable[[StringSource], StringSource]]]:
    return [
        NameAndValue(
            'SingleNonNegIntSource',
            mk_SingleNonNegIntSource,
        ),
        NameAndValue(
            'SingleNegIntSource',
            mk_SingleNegIntSource,
        ),
        NameAndValue(
            'UpperNonNegLimitSource',
            mk_UpperNonNegLimitSource,
        ),
        NameAndValue(
            'UpperNegLimitSource',
            mk_UpperNegLimitSource,
        ),
        NameAndValue(
            'LowerNonNegLimitSource',
            mk_LowerNonNegLimitSource,
        ),
        NameAndValue(
            'LowerNegLimitSource',
            mk_LowerNegLimitSource,
        ),
        NameAndValue(
            'LowerNonNegUpperNonNegSource',
            mk_LowerNonNegUpperNonNegSource,
        ),
        NameAndValue(
            'LowerNonNegUpperNegSource',
            mk_LowerNonNegUpperNegSource,
        ),
        NameAndValue(
            'LowerNegUpperNonNegSource',
            mk_LowerNegUpperNonNegSource,
        ),
        NameAndValue(
            'LowerNegUpperNegSource',
            mk_LowerNegUpperNegSource,
        ),
        NameAndValue(
            'SegmentsSource',
            mk_SegmentsSource,
        ),
    ]


def mk_SingleNonNegIntSource(transformed: StringSource) -> StringSource:
    return sut.single_non_neg_int_source(_MEM_BUFF_SIZE, _transformer_description, transformed, 0)


def mk_SingleNegIntSource(transformed: StringSource) -> StringSource:
    return sut.single_neg_int_source(_MEM_BUFF_SIZE, _transformer_description, transformed, -1)


def mk_UpperNonNegLimitSource(transformed: StringSource) -> StringSource:
    return sut.upper_non_neg_limit_source(_MEM_BUFF_SIZE, _transformer_description, transformed, 0)


def mk_UpperNegLimitSource(transformed: StringSource) -> StringSource:
    return sut.upper_neg_limit_source(_MEM_BUFF_SIZE, _transformer_description, transformed, -1)


def mk_LowerNonNegLimitSource(transformed: StringSource) -> StringSource:
    return sut.lower_non_neg_limit_source(_MEM_BUFF_SIZE, _transformer_description, transformed, 0)


def mk_LowerNegLimitSource(transformed: StringSource) -> StringSource:
    return sut.lower_neg_limit_source(_MEM_BUFF_SIZE, _transformer_description, transformed, -1)


def mk_LowerNonNegUpperNonNegSource(transformed: StringSource) -> StringSource:
    return sut.lower_non_neg_upper_non_neg_source(_MEM_BUFF_SIZE, _transformer_description, transformed, 0, 1)


def mk_LowerNonNegUpperNegSource(transformed: StringSource) -> StringSource:
    return sut.lower_non_neg_upper_neg_source(_MEM_BUFF_SIZE, _transformer_description, transformed, 0, -1)


def mk_LowerNegUpperNonNegSource(transformed: StringSource) -> StringSource:
    return sut.lower_neg_upper_non_neg_source(_MEM_BUFF_SIZE, _transformer_description, transformed, -1, 1)


def mk_LowerNegUpperNegSource(transformed: StringSource) -> StringSource:
    return sut.lower_neg_upper_neg_source(_MEM_BUFF_SIZE, _transformer_description, transformed, -2, -1)


def mk_SegmentsSource(transformed: StringSource) -> StringSource:
    return sut.segments_source(_MEM_BUFF_SIZE, _transformer_description,
                               transformed,
                               SegmentsWithPositiveIncreasingValues(1, [(3, 4)], None)
                               )


class Case:
    def __init__(self,
                 name: str,
                 transformer: Callable[[StringSource], StringSource],
                 source_model_contents: str,
                 source_model_method_invocations: ValueAssertion[Sequence[StringSourceMethod]],
                 ):
        self.name = name
        self.transformer = transformer
        self.source_model_contents = source_model_contents
        self.source_model_method_invocations = source_model_method_invocations


def multiple_ranges_w_negative_values_cases() -> Sequence[Case]:
    return [
        Case(
            'empty',
            lambda source: mk_MultipleRangesWNegativeValues(
                source,
                [SingleLineRange(-10)],
                range_merge.Partitioning([10], [], [])
            ),
            '1st\n2nd\n3rd\n',
            asrt.equals([StringSourceMethod.FREEZE,
                         StringSourceMethod.AS_LINES,
                         StringSourceMethod.AS_LINES]),
        ),
        Case(
            'everything',
            lambda source: mk_MultipleRangesWNegativeValues(
                source,
                [SingleLineRange(-1)],
                range_merge.Partitioning([1, 2], [], [])
            ),
            '1st\n2nd\n3rd\n',
            asrt.equals([StringSourceMethod.FREEZE,
                         StringSourceMethod.AS_LINES,
                         StringSourceMethod.AS_LINES]),
        ),
        Case(
            'some, but not all, lines',
            lambda source: mk_MultipleRangesWNegativeValues(
                source,
                [SingleLineRange(-1)],
                range_merge.Partitioning([1], [], [])
            ),
            '1st\n2nd\n3rd\n',
            asrt.equals([StringSourceMethod.FREEZE,
                         StringSourceMethod.AS_LINES,
                         StringSourceMethod.AS_LINES]),
        ),
    ]


def mk_MultipleRangesWNegativeValues(transformed: StringSource,
                                     negatives: List[Range],
                                     partial_partitioning: range_merge.Partitioning,
                                     ) -> StringSource:
    return sut.multiple_ranges_w_negative_values(
        _MEM_BUFF_SIZE,
        _transformer_description,
        transformed,
        negatives,
        partial_partitioning,
    )


_MEM_BUFF_SIZE = 2 ** 10


def _transformer_description() -> StructureRenderer:
    return renderers.header_only('the header')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
