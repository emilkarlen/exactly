import shlex
import unittest

from exactly_lib.impls import file_properties
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.files_matcher import parse_files_matcher as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as args, \
    integration_check
from exactly_lib_test.impls.types.files_matcher.test_resources import expression
from exactly_lib_test.impls.types.files_matcher.test_resources import model
from exactly_lib_test.impls.types.files_matcher.test_resources import test_case_bases
from exactly_lib_test.impls.types.files_matcher.test_resources.arguments_building import \
    FileQuantificationAssertionVariant, FilesMatcherArgumentsSetup, \
    files_matcher_setup_without_references
from exactly_lib_test.impls.types.files_matcher.test_resources.check_with_neg_and_rel_opts import \
    MatcherChecker
from exactly_lib_test.impls.types.files_matcher.test_resources.model import arbitrary_model
from exactly_lib_test.impls.types.files_matcher.test_resources.quant_over_files.arguments import file_contents_arg2
from exactly_lib_test.impls.types.files_matcher.test_resources.quant_over_files.misc import \
    FileMatcherThatMatchesAnyFileWhosNameStartsWith
from exactly_lib_test.impls.types.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as sm_arg
from exactly_lib_test.impls.types.string_transformer.test_resources import test_transformers_setup
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    PassOrFail, expectation_type_config__non_is_success
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir, sym_link
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    equals_symbol_references__w_str_rendering
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.symbol_context import FileMatcherSymbolContext, \
    FileMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestSymbolReferences),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),

        unittest.makeSuite(TestFileMatcherShouldBeValidated),
        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines),

        unittest.makeSuite(TestHardErrorWhenContentsOfAFileThatIsNotARegularFileIsTested),

        unittest.makeSuite(TestExistsContentsEmptyFile),
        unittest.makeSuite(TestForAllContentsEmptyFile),
        unittest.makeSuite(TestExistsTypeDir),

        unittest.makeSuite(TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked),

        unittest.makeSuite(TestAssertionVariantThatTransformersMultipleFiles),
    ])


class TestWithAssertionVariantForFileContents(test_case_bases.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return files_matcher_setup_without_references(
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.Empty()),
            )
        )


class TestParseInvalidSyntax(test_case_bases.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForFileContents):
    pass


class TestFileMatcherShouldBeValidated(unittest.TestCase):
    def test(self):
        symbol_name = 'the_string_matcher'
        for quantifier in Quantifier:
            arguments = args.Quantification(
                quantifier,
                fm_args.SymbolReference(symbol_name))

            for case in validation_cases.failing_validation_cases(symbol_name):
                symbol_context = case.value.symbol_context

                with self.subTest(quantifier=quantifier,
                                  validation_case=case.name):
                    integration_check.CHECKER__PARSE_FULL.check(
                        self,
                        source=remaining_source(str(arguments)),
                        input_=arbitrary_model(),
                        arrangement=
                        Arrangement(
                            symbols=symbol_context.symbol_table
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=symbol_context.references_assertion,
                            ),
                            ExecutionExpectation(
                                validation=case.value.expectation,
                            ),
                        ),
                    )


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        checked_dir_rel_conf = relativity_options.conf_rel_any(RelOptionType.REL_ACT)
        checked_dir_populator = checked_dir_rel_conf.populator_for_relativity_option_root(
            DirContents([
                File.empty('a-file-so-that-checked-dir-is-not-empty')
            ]
            )
        )

        file_matcher = FileMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER',
            True,
        )
        after_bin_op = 'after bin op'
        fm_argument = fm_args.conjunction([
            fm_args.SymbolReference(file_matcher.name),
            fm_args.Custom(after_bin_op),
        ])
        # ACT & ASSERT #
        for quantifier in Quantifier:
            arguments = args.Quantification(quantifier, fm_argument)
            with self.subTest(quantifier):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    source=arguments.as_remaining_source,
                    input_=model.model_constructor__non_recursive(
                        path_sdvs.of_rel_option(checked_dir_rel_conf.relativity)
                    ),
                    arrangement=arrangement_w_tcds(
                        symbols=file_matcher.symbol_table,
                        tcds_contents=checked_dir_populator
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_line(
                                current_line_number=1,
                                remaining_part_of_current_line=fm_argument.operator + ' ' + after_bin_op),
                            symbol_references=file_matcher.references_assertion
                        ),
                        ExecutionExpectation(
                            main_result=asrt_matching_result.matches_value(file_matcher.result_value)
                        )
                    ),
                )


class TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.parsers().full,
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumLinesCheck(),
                                        invalid_integers_according_to_custom_validation=[-1, -2])


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumLinesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparison condition string.
    """

    def apply(self, condition_str: str) -> str:
        arguments_constructor = args.complete_arguments_constructor(
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.NumLines(condition_str))))
        return arguments_constructor.apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))


class TestSymbolReferences(test_case_bases.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForFileContents):
    def test_symbols_from_contents_assertion_SHOULD_be_reported(self):
        # ARRANGE #

        operand_sym_ref = SymbolReference('operand_symbol_name',
                                          is_string__all_indirect_refs_are_strings())

        condition_str = '{operator} {symbol_reference}'.format(
            operator=comparators.EQ.name,
            symbol_reference=symbol_reference_syntax_for_name(operand_sym_ref.name)
        )
        arguments_constructor = args.complete_arguments_constructor(
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.NumLines(condition_str))))

        argument = arguments_constructor.apply(
            expectation_type_config__non_is_success(ExpectationType.NEGATIVE)
        )

        source = remaining_source(argument)

        # ACT #

        matcher_sdv = sut.parsers().full.parse(source)

        assert isinstance(matcher_sdv, MatcherSdv)

        actual_symbol_references = matcher_sdv.references

        # ASSERT #

        expected_symbol_references = [
            operand_sym_ref,
        ]
        assertion = equals_symbol_references__w_str_rendering(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestHardErrorWhenContentsOfAFileThatIsNotARegularFileIsTested(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    file_content_assertion_variants = [
        sm_arg.Empty(),
        sm_arg.NumLines(int_condition(comparators.NE, 0)),
        sm_arg.Equals.eq_string('expected'),
    ]

    def test_hard_error_when_there_is_a_single_file_that_is_not_a_regular_file(self):
        name_of_checked_dir = 'checked-dir'
        relativity_root_conf = rel_opt_conf.default_conf_rel_any(RelOptionType.REL_CWD)
        the_model = model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir)(relativity_root_conf)

        non_regular_files = [
            Dir.empty('a-directory'),
            sym_link('sym-link', 'non-existing-target')
        ]

        for file_contents_assertion in self.file_content_assertion_variants:
            for quantifier in Quantifier:
                arguments_constructor = args.complete_arguments_constructor(
                    FileQuantificationAssertionVariant(
                        quantifier,
                        file_contents_arg2(file_contents_assertion)))
                for expectation_type in ExpectationType:
                    arguments = arguments_constructor.apply(
                        expectation_type_config__non_is_success(expectation_type))
                    for non_regular_file in non_regular_files:
                        with self.subTest(
                                quantifier=quantifier.name,
                                expectation_type=expectation_type.name,
                                arguments=arguments,
                                non_regular_file=non_regular_file.name):
                            integration_check.CHECKER__PARSE_FULL.check(
                                self,
                                remaining_source(arguments),
                                the_model,
                                arrangement=
                                arrangement_w_tcds(
                                    tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                        DirContents([
                                            Dir(name_of_checked_dir, [
                                                non_regular_file,
                                            ]),
                                        ])
                                    )
                                ),
                                expectation=
                                Expectation(
                                    execution=ExecutionExpectation(
                                        is_hard_error=asrt.anything_goes()
                                    ),
                                )
                            )


AN_ACCEPTED_SDS_REL_OPT_CONFIG = rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_TMP)


class TestExistsContentsEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    exists__empty__arguments = args.complete_arguments_constructor(
        FileQuantificationAssertionVariant(
            Quantifier.EXISTS,
            file_contents_arg2(sm_arg.Empty()))
    )

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.parsers().full)

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            main_result_for_positive_expectation=PassOrFail.PASS,
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_no_files(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestExistsTypeDir(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    exists__type_dir__arguments = args.complete_arguments_constructor(
        FileQuantificationAssertionVariant(
            Quantifier.EXISTS,
            fm_args.WithOptionalNegation(fm_args.Type(file_properties.FileType.DIRECTORY)))
    )

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.parsers().full)

    def test_one_dir_and_one_regular(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__type_dir__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            main_result_for_positive_expectation=PassOrFail.PASS,
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('regular.txt'),
                    Dir.empty('dir'),
                ]),
            ]),
        )

    def test_just_one_regular(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__type_dir__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('regular.txt'),
                ]),
            ]),
        )


class TestForAllContentsEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    for_all__empty__arguments = args.complete_arguments_constructor(
        FileQuantificationAssertionVariant(
            Quantifier.ALL,
            file_contents_arg2(sm_arg.Empty()))
    )

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.parsers().full)

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            main_result_for_positive_expectation=PassOrFail.FAIL,
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File.empty('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_no_files(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked(unittest.TestCase):
    file_content_assertion_variants_that_pass_iff_file_is_empty = [
        sm_arg.Empty(),
        sm_arg.NumLines(int_condition(comparators.EQ, 0)),
        sm_arg.Equals.eq_string(shlex.quote('')),
    ]

    def test__all__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = FileMatcherSymbolContext.of_primitive(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            File.empty('selected-empty-file.txt'),
            File(
                'un-selected-non-empty-file.txt', 'contents of non-emtpy file'),
            Dir.empty('un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = name_starts_with_selected.symbol_table
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_file_matcher(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for pass_iff_file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                FileQuantificationAssertionVariant(
                    Quantifier.ALL,
                    file_contents_arg2(pass_iff_file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type)
                arguments = arguments_constructor.apply(etc)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    integration_check.CHECKER__PARSE_FULL.check(
                        self,
                        remaining_source(arguments),
                        model.model_with_source_path_as_sub_dir_of_rel_root(name_of_checked_dir)(relativity_root_conf),
                        arrangement=
                        arrangement_w_tcds(
                            tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=expected_symbol_references,
                            ),
                            ExecutionExpectation(
                                main_result=etc.pass__if_positive__fail__if_negative,
                            ),
                        )
                    )

    def test__exists__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = FileMatcherSymbolContext.of_primitive(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            File(
                'selected-non-empty-file.txt', 'contents of non-emtpy file'),
            File.empty('un-selected-empty-file.txt'),
            Dir.empty('un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = name_starts_with_selected.symbol_table
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_file_matcher(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                FileQuantificationAssertionVariant(
                    Quantifier.EXISTS,
                    file_contents_arg2(file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type)
                arguments = arguments_constructor.apply(etc)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    integration_check.CHECKER__PARSE_FULL.check(
                        self,
                        remaining_source(arguments),
                        model.model_with_source_path_as_sub_dir_of_rel_root(name_of_checked_dir)(relativity_root_conf),
                        arrangement=
                        arrangement_w_tcds(
                            tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=expected_symbol_references
                            ),
                            ExecutionExpectation(
                                main_result=etc.fail__if_positive__pass_if_negative,
                            ),
                        )
                    )


class TestAssertionVariantThatTransformersMultipleFiles(unittest.TestCase):
    """
    The "equals" assertion variant needs to create intermediate files (as of 2017-09-17).
    This means that the integration of the file contents assertion ("equals") must provide
    the ability to create these files.

    The difference between the "file contents" and "dir contents"
    case is that multiple intermediate files may need to be created by "dir contents".
    """
    name_of_checked_dir = 'checked-dir'

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.parsers().full)

    def test_it_SHOULD_be_possible_to_create_multiple_intermediate_files(self):
        # ARRANGE #
        original_file_contents = 'original_file_contents'
        expected_transformer_contents = original_file_contents.upper()

        transform_to_uppercase = test_transformers_setup.TO_UPPER_CASE_TRANSFORMER

        symbol_table_with_lines_transformer = transform_to_uppercase.symbol_table
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(transform_to_uppercase.name)
        ])

        for_all__equals__arguments = args.complete_arguments_constructor(
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.Transformed(transform_to_uppercase.name,
                                                      sm_arg.Equals.eq_string(expected_transformer_contents)))
                ,
            ))
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG
        etc = expectation_type_config__non_is_success(ExpectationType.POSITIVE)
        arguments = for_all__equals__arguments.apply(etc)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check(
            self,
            remaining_source(arguments),
            model.model_with_rel_root_as_source_path(relativity_root_conf),
            arrangement=
            arrangement_w_tcds(
                tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                    DirContents([
                        File('1.txt', original_file_contents),
                        File('2.txt', original_file_contents),
                    ])
                ),
                symbols=symbol_table_with_lines_transformer
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_references
                ),
                ExecutionExpectation(
                    main_result=etc.pass__if_positive__fail__if_negative,
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
