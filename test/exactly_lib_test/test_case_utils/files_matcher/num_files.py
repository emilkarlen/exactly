import unittest

from exactly_lib.definitions import logic
from exactly_lib.tcfs.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import expression
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import model
from exactly_lib_test.test_case_utils.files_matcher.test_resources import test_case_bases
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    NumFilesAssertionVariant, argument_constructor_for_num_files_check, \
    FilesMatcherArgumentsSetup, files_matcher_setup_without_references
from exactly_lib_test.test_case_utils.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.test_case_utils.integer_matcher.test_resources import argument_building as im_args
from exactly_lib_test.test_case_utils.integer_matcher.test_resources import symbol_reference
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opts
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.files.file_structure import Dir, DirContents, File
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringIntConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestDifferentSourceVariants),
        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgument),
    ])


class TestWithAssertionVariantForNumFiles(test_case_bases.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return files_matcher_setup_without_references(
            NumFilesAssertionVariant(int_condition(comparators.EQ, 0))
        )


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return '{num_files} {condition}'.format(
            num_files=config.NUM_FILES_CHECK_ARGUMENT,
            condition=condition_str)


class TestParseInvalidSyntax(test_case_bases.TestParseInvalidSyntaxWithMissingSelectorArgCaseBase,
                             TestWithAssertionVariantForNumFiles):
    pass


class TestFailingValidationPreSdsDueToInvalidIntegerArgument(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.parsers().full,
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(),
                                        invalid_integers_according_to_custom_validation=[-1, -2])


class TestSymbolReferences(test_case_bases.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForNumFiles):
    def test_symbols_from_comparison_SHOULD_be_reported(self):
        # ARRANGE #
        checked_dir_contents = DirContents([File.empty('1'), File.empty('2')])
        checked_path = rel_opts.conf_rel_sds(RelSdsOptionType.REL_ACT)

        operand_sym_ref = StringIntConstantSymbolContext(
            'operand_symbol_name',
            len(checked_dir_contents.file_system_elements),
            default_restrictions=symbol_reference.is_integer_expression_string(),
        )

        matcher_arguments = im_args.comparison(comparators.EQ,
                                               operand_sym_ref.argument)

        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumFiles(
                matcher_arguments.as_str,
                int_expr_on_new_line=True,
            ).as_remaining_source,
            model.model_with_rel_root_as_source_path(checked_path),
            arrangement_w_tcds(
                symbols=operand_sym_ref.symbol_table,
                tcds_contents=checked_path.populator_for_relativity_option_root(checked_dir_contents),
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(2),
                    symbol_references=operand_sym_ref.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            )
        )

    def test_matcher_symbol_should_be_reported(self):
        # ARRANGE #
        matcher_symbol = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER_SYMBOL',
            True,
        )

        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumFiles(
                matcher_symbol.name__sym_ref_syntax,
                int_expr_on_new_line=True,
            ).as_remaining_source,
            model.arbitrary_model(),
            arrangement_w_tcds(
                symbols=matcher_symbol.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(2),
                    symbol_references=matcher_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(matcher_symbol.result_value)
                ),
            )
        )


class TestDifferentSourceVariants(test_case_bases.TestCaseBaseForParser):
    def test_integer_transformer_should_be_parsed_as_simple_expression(self):
        # ARRANGE #
        after_lhs_expression = logic.AND_OPERATOR_NAME + ' after bin op'
        matcher_symbol = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER_SYMBOL',
            True,
        )
        complex_expression = ' '.join((matcher_symbol.name__sym_ref_syntax,
                                       after_lhs_expression))
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumFiles(
                complex_expression,
            ).as_remaining_source,
            model.arbitrary_model(),
            arrangement_w_tcds(
                symbols=matcher_symbol.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=after_lhs_expression,
                    ),
                    symbol_references=matcher_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(matcher_symbol.result_value)
                ),
            )
        )

    def test_file_is_directory_that_has_expected_number_of_files(self):
        directory_with_one_file = Dir('name-of-dir', [File.empty('a-file-in-checked-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            int_condition(comparators.EQ, 1)
        )

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            model.model_with_source_path_as_sub_dir_of_rel_root(directory_with_one_file.name),
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_a_directory_that_has_unexpected_number_of_files(self):
        directory_with_one_file = Dir('name-of-non-empty-dir',
                                      [File.empty('file-in-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            int_condition(comparators.EQ, 2)
        )

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            model.model_with_source_path_as_sub_dir_of_rel_root(directory_with_one_file.name),
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_directory_with_files_but_none_that_matches_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern_that_matches_exactly_one_file = 'a*'

        dir_with_two_files = Dir(name_of_directory,
                                 [
                                     File.empty('a file'),
                                     File.empty('b file'),
                                 ])

        contents_of_relativity_option_root = DirContents([dir_with_two_files])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            int_condition(comparators.EQ, 1),
            name_option_pattern=pattern_that_matches_exactly_one_file)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            model.model_with_source_path_as_sub_dir_of_rel_root(name_of_directory),
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_integer_matcher_on_new_line(self):
        # ARRANGE #
        checked_dir_contents = DirContents([File.empty('1'), File.empty('2')])
        checked_path = rel_opts.conf_rel_sds(RelSdsOptionType.REL_ACT)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumFiles(
                int_condition(comparators.EQ,
                              len(checked_dir_contents.file_system_elements)),
                int_expr_on_new_line=True,
            ).as_remaining_source,
            model.model_with_rel_root_as_source_path(checked_path),
            arrangement_w_tcds(
                tcds_contents=checked_path.populator_for_relativity_option_root(checked_dir_contents),
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(2)
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
