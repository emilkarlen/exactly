import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.file_matcher.file_matcher_ddvs import FileMatcherDdvFromParts
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherConstant
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to__ref, \
    FileMatcherResolverConstantValueTestImpl
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.condition.integer.test_resources import arguments_building as int_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax as fm_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fsm_args, model
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_confs, matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import ValidatorThat
from exactly_lib_test.test_resources.files.file_structure import Dir, empty_file, DirContents
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferenceFromBothSelectorAndFilesMatcherShouldBeReported(),
        TestFileMatcherShouldBeValidated(),
        TestSequenceOfSelectionsAreCombinedWithAnd(),
    ])


class TestSymbolReferenceFromBothSelectorAndFilesMatcherShouldBeReported(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        name_of_referenced_selector = 'SELECTOR'
        name_of_referenced_files_matcher = 'FILES_MATCHER'

        expected_symbol_usages = asrt.matches_sequence([
            is_file_matcher_reference_to__ref(name_of_referenced_selector),
            is_reference_to_files_matcher__ref(name_of_referenced_files_matcher),
        ])

        arguments = fsm_args.argument_constructor_for_symbol_reference(
            files_matcher_symbol_name=name_of_referenced_files_matcher,
            named_matcher=name_of_referenced_selector
        ).apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))

        source = remaining_source(arguments)

        # ACT #

        resolver = sut.files_matcher_parser().parse(source)

        # ASSERT #

        expected_symbol_usages.apply_without_message(self,
                                                     resolver.references)


class TestFileMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        err_msg_from_validator = 'error from validator'

        name_of_referenced_symbol = 'FILE_MATCHER_WITH_VALIDATION_FAILURE'

        expected_symbol_usages = asrt.matches_sequence(
            [is_file_matcher_reference_to__ref(name_of_referenced_symbol)])

        selection_is_empty_arguments = fsm_args.argument_constructor_for_emptiness_check(
            named_matcher=name_of_referenced_symbol
        ).apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))

        def get_file_matcher_successful_matcher(tcds: Tcds) -> FileMatcher:
            return FileMatcherConstant(True)

        cases = [
            NEA('pre sds validation',
                expected=
                Expectation(
                    validation_pre_sds=asrt_validation.matches_validation_failure(asrt.equals(err_msg_from_validator)),
                    symbol_usages=expected_symbol_usages,
                ),
                actual=
                ValidatorThat(
                    pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                )
                ),
            NEA('post sds validation',
                expected=
                Expectation(
                    validation_post_sds=asrt_validation.matches_validation_failure(asrt.equals(err_msg_from_validator)),
                    symbol_usages=expected_symbol_usages,
                ),
                actual=
                ValidatorThat(
                    post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                )
                ),
        ]

        for case in cases:
            resolver_of_failing_matcher = FileMatcherResolverConstantValueTestImpl(
                FileMatcherDdvFromParts(
                    case.actual,
                    get_file_matcher_successful_matcher
                ),
                (),
            )
            symbols = SymbolTable({
                name_of_referenced_symbol: container(resolver_of_failing_matcher),
            })

            selection_is_empty_source = remaining_source(selection_is_empty_arguments)

            # ACT & ASSERT #
            with self.subTest(case.name):
                integration_check.check(
                    self,
                    sut.files_matcher_parser(),
                    selection_is_empty_source,
                    model.arbitrary_model(),
                    ArrangementPostAct(
                        symbols=symbols,
                    ),
                    expectation=case.expected
                )


class TestSequenceOfSelectionsAreCombinedWithAnd(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        positive_expectation = expectation_type_config__non_is_success(ExpectationType.POSITIVE)
        rel_opt_conf = rel_opt_confs.conf_rel_sds(RelSdsOptionType.REL_TMP)
        parser = sut.files_matcher_parser()

        # dir contents

        checked_dir = Dir('checked-dir', [
            empty_file('a.x'),
            empty_file('a.y'),
            empty_file('b.x'),
            empty_file('b.y'),
        ])

        # arguments

        file_matcher_arg__begins_with_a = fm_args.file_matcher_arguments(
            name_pattern='a*'
        )

        file_matcher_arg__ends_with_x = fm_args.file_matcher_arguments(
            name_pattern='*.x'
        )

        files_matcher_args__num_files_eq_1 = fsm_args.NumFilesAssertionVariant(
            int_args.int_condition(comparators.EQ, 1)
        )

        files_matcher_args__num_files_ending_with_x_eq_1 = fsm_args.SelectionAndMaterArgumentsConstructor(
            file_matcher_arg__ends_with_x,
            files_matcher_args__num_files_eq_1,
        )

        files_matcher_source__num_files_ending_with_x_eq_1 = files_matcher_args__num_files_ending_with_x_eq_1.apply(
            positive_expectation
        )

        symbol_name = 'FILES_MATCHER_SYMBOL'

        files_matcher_args__begins_with_a__symbol = fsm_args.SelectionAndMaterArgumentsConstructor(
            file_matcher_arg__begins_with_a,
            fsm_args.symbol_reference(symbol_name),
        )
        files_matcher_source__begins_with_a__symbol = files_matcher_args__begins_with_a__symbol.apply(
            positive_expectation
        )

        # ACT #

        num_files_ending_with_x_eq_1_resolver = parser.parse(
            remaining_source(files_matcher_source__num_files_ending_with_x_eq_1)
        )

        symbols = SymbolTable({
            symbol_name: container(num_files_ending_with_x_eq_1_resolver),
        })

        # ASSERT #

        integration_check.check(
            self,
            parser,
            remaining_source(files_matcher_source__begins_with_a__symbol),
            model.model_with_source_path_as_sub_dir_of_rel_root(checked_dir.name)(rel_opt_conf),
            ArrangementPostAct(
                sds_contents=rel_opt_conf.populator_for_relativity_option_root__sds(
                    DirContents([checked_dir])
                ),
                symbols=symbols,
            ),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    is_reference_to_files_matcher__ref(symbol_name)
                ]),
                main_result=matcher_assertions.is_matching_success(),
            )
        )
