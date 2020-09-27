import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.tcfs.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import files_matcher as files_matcher_test_impl
from exactly_lib_test.symbol.test_resources.file_matcher import is_reference_to_file_matcher, \
    FileMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.condition.integer.test_resources import arguments_building as int_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args2, validation_cases
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax as fm_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args, \
    integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fsm_args, model
from exactly_lib_test.test_case_utils.files_matcher.test_resources.parsers import TOP_LEVEL_PARSER_CASES
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_confs, matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.test_resources.files.file_structure import Dir, DirContents, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFileMatcherShouldBeParsedAsSimpleExpression(),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
        TestSymbolReferenceFromBothSelectorAndFilesMatcherShouldBeReported(),
        TestFileMatcherShouldBeValidated(),
        TestSequenceOfSelectionsAreCombinedWithAnd(),
    ])


class TestFileMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        file_matcher_argument = fm_args2.conjunction(
            [
                fm_args2.SymbolReferenceWReferenceSyntax('FILE_MATCHER_SYMBOL_1'),
                fm_args2.SymbolReferenceWReferenceSyntax('FILE_MATCHER_SYMBOL_2'),
            ],
        )
        files_matcher_argument = args.Empty()

        arguments = args.Selection(
            file_matcher_argument,
            files_matcher_argument
        )
        for top_level_parser_case in TOP_LEVEL_PARSER_CASES:
            with self.subTest(top_level_parser_case.name):
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    top_level_parser_case.value.parse(arguments.as_remaining_source)


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = DirContents([File.empty('a file making the model non-empty')])

        file_matcher = FileMatcherSymbolContextOfPrimitiveConstant(
            'FILE_MATCHER_SYMBOL',
            True,
        )
        files_matcher__parsed = FilesMatcherSymbolContext.of_primitive(
            'FILES_MATCHER_1',
            files_matcher_test_impl.FilesMatcherNumFilesTestImpl(
                len(model_contents.file_system_elements)
            )
        )
        symbols = [file_matcher, files_matcher__parsed]

        files_matcher_bin_op_expr = args.conjunction([
            fm_args2.SymbolReferenceWReferenceSyntax(files_matcher__parsed.name),
            args.Custom('after bin op'),
        ])

        arguments = fsm_args.Selection(
            fm_args2.SymbolReferenceWReferenceSyntax(file_matcher.name),
            files_matcher_bin_op_expr,
        )
        model_rel_opt_conf = rel_opt_confs.conf_rel_any(RelOptionType.REL_ACT)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            arguments.as_remaining_source,
            model.model_with_rel_root_as_source_path(model_rel_opt_conf),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds_contents=model_rel_opt_conf.populator_for_relativity_option_root(model_contents)
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=' '.join([
                            files_matcher_bin_op_expr.operator,
                            files_matcher_bin_op_expr.operands[1].as_str,
                        ])
                    ),
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                ),
                ExecutionExpectation(
                    main_result=matcher_assertions.is_matching_success(),
                ),
            ),
        )


class TestSymbolReferenceFromBothSelectorAndFilesMatcherShouldBeReported(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        name_of_referenced_selector = 'SELECTOR'
        name_of_referenced_files_matcher = 'FILES_MATCHER'

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_file_matcher(name_of_referenced_selector),
            is_reference_to_files_matcher(name_of_referenced_files_matcher),
        ])

        arguments = fsm_args.argument_constructor_for_symbol_reference(
            files_matcher_symbol_name=name_of_referenced_files_matcher,
            named_matcher=name_of_referenced_selector
        ).apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))

        source = remaining_source(arguments)

        # ACT #

        sdv = sut.parsers().full.parse(source)

        # ASSERT #

        expected_symbol_usages.apply_without_message(self,
                                                     sdv.references)


class TestFileMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        name_of_referenced_symbol = 'FILE_MATCHER_WITH_VALIDATION_FAILURE'

        selection_is_empty_arguments = fsm_args.Selection(
            fm_args2.SymbolReference(name_of_referenced_symbol),
            args.Empty()
        )

        for case in validation_cases.failing_validation_cases(name_of_referenced_symbol):
            symbol_context = case.value.symbol_context

            selection_is_empty_source = selection_is_empty_arguments.as_remaining_source

            # ACT & ASSERT #
            with self.subTest(case.name):
                integration_check.CHECKER__PARSE_FULL.check(
                    self,
                    selection_is_empty_source,
                    model.arbitrary_model(),
                    arrangement_w_tcds(
                        symbols=symbol_context.symbol_table,
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=symbol_context.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestSequenceOfSelectionsAreCombinedWithAnd(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        positive_expectation = expectation_type_config__non_is_success(ExpectationType.POSITIVE)
        rel_opt_conf = rel_opt_confs.conf_rel_sds(RelSdsOptionType.REL_TMP)
        parser = sut.parsers().full

        # dir contents

        checked_dir = Dir('checked-dir', [
            File.empty('a.x'),
            File.empty('a.y'),
            File.empty('b.x'),
            File.empty('b.y'),
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

        files_matcher_args__num_files_ending_with_x_eq_1 = fsm_args.SelectionAndMatcherArgumentsConstructor(
            file_matcher_arg__ends_with_x,
            files_matcher_args__num_files_eq_1,
        )

        files_matcher_source__num_files_ending_with_x_eq_1 = files_matcher_args__num_files_ending_with_x_eq_1.apply(
            positive_expectation
        )

        symbol_name = 'FILES_MATCHER_SYMBOL'

        files_matcher_args__begins_with_a__symbol = fsm_args.SelectionAndMatcherArgumentsConstructor(
            file_matcher_arg__begins_with_a,
            fsm_args.symbol_reference(symbol_name),
        )
        files_matcher_source__begins_with_a__symbol = files_matcher_args__begins_with_a__symbol.apply(
            positive_expectation
        )

        num_files_ending_with_x_eq_1_resolver = parser.parse(
            remaining_source(files_matcher_source__num_files_ending_with_x_eq_1)
        )

        symbols = FilesMatcherSymbolContext.of_sdv(symbol_name,
                                                   num_files_ending_with_x_eq_1_resolver,
                                                   ).symbol_table

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            remaining_source(files_matcher_source__begins_with_a__symbol),
            model.model_with_source_path_as_sub_dir_of_rel_root(checked_dir.name)(rel_opt_conf),
            arrangement_w_tcds(
                non_hds_contents=rel_opt_conf.populator_for_relativity_option_root__sds(
                    DirContents([checked_dir])
                ),
                symbols=symbols,
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_files_matcher(symbol_name)
                    ]),
                ),
                ExecutionExpectation(
                    main_result=matcher_assertions.is_matching_success(),
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
