import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.condition.integer.test_resources import arguments_building as int_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax as fm_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fsm_args, model
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_confs, matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.test_resources.files.file_structure import Dir, empty_file, DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSequenceOfSelectionsAreCombinedWithAnd(),
    ])


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
