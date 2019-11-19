import shlex
import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherConstantSdv
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import instruction_arguments as args
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import tr
from exactly_lib_test.instructions.assert_.test_resources import expression, instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    FileQuantificationAssertionVariant, FilesMatcherArgumentsSetup, \
    files_matcher_setup_without_references
from exactly_lib_test.test_case_utils.files_matcher.test_resources.quant_over_files.arguments import file_contents_arg2
from exactly_lib_test.test_case_utils.files_matcher.test_resources.quant_over_files.misc import \
    FileMatcherThatMatchesAnyFileWhosNameStartsWith
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building2 as sm_arg
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.contents_transformation import \
    ToUppercaseStringTransformer
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, pfh_expectation_type_config
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, File, Dir, empty_dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestCommonFailureConditions),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines),

        unittest.makeSuite(TestHardErrorWhenAFileThatIsNotARegularFileIsTested),

        unittest.makeSuite(TestRelativityVariantsOfCheckedDir),

        unittest.makeSuite(TestExistsEmptyFile),
        unittest.makeSuite(TestForAllEmptyFile),

        unittest.makeSuite(TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked),

        unittest.makeSuite(TestAssertionVariantThatTransformersMultipleFiles),
    ])


class TestWithAssertionVariantForFileContents(tr.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return files_matcher_setup_without_references(
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.Empty()),
            )
        )


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForFileContents):
    pass


class TestCommonFailureConditions(tr.TestCommonFailureConditionsBase,
                                  TestWithAssertionVariantForFileContents):
    pass


class TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.parser.Parser(),
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(),
                                        invalid_integers_according_to_custom_validation=[-1, -2])

    def test_invalid_integer_argument_according_to_custom_validation(self):
        super().test_invalid_integer_argument_according_to_custom_validation()


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self, condition_str: str) -> str:
        arguments_constructor = args.complete_arguments_constructor(
            'ignored-dir-path',
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.NumLines(condition_str))))
        return arguments_constructor.apply(pfh_expectation_type_config(ExpectationType.POSITIVE),
                                           tr.DEFAULT_REL_OPT_CONFIG)


class TestSymbolReferences(tr.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForFileContents):
    def test_symbols_from_contents_assertion_SHOULD_be_reported(self):
        # ARRANGE #

        operand_sym_ref = SymbolReference('operand_symbol_name',
                                          string_made_up_by_just_strings())

        condition_str = '{operator} {symbol_reference}'.format(
            operator=comparators.EQ.name,
            symbol_reference=symbol_reference_syntax_for_name(operand_sym_ref.name)
        )
        arguments_constructor = args.complete_arguments_constructor(
            'ignored-dir-path',
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.NumLines(condition_str))))

        argument = arguments_constructor.apply(pfh_expectation_type_config(ExpectationType.NEGATIVE),
                                               tr.DEFAULT_REL_OPT_CONFIG)

        source = remaining_source(argument)

        # ACT #

        actual_instruction = sut.parser.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)

        assert isinstance(actual_instruction, AssertPhaseInstruction)

        actual_symbol_references = actual_instruction.symbol_usages()

        # ASSERT #

        expected_symbol_references = [
            operand_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestRelativityVariantsOfCheckedDir(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    arguments_constructor_for_emptiness = args.complete_arguments_constructor(
        name_of_checked_dir,
        FileQuantificationAssertionVariant(
            Quantifier.ALL,
            file_contents_arg2(sm_arg.Empty())))

    @property
    def instruction_checker(self) -> InstructionChecker:
        return InstructionChecker(self, sut.parser.Parser(), tr.ACCEPTED_REL_OPT_CONFIGURATIONS)

    def test_just_one_empty_file(self):
        self.instruction_checker.check_rel_opt_variants_and_expectation_type_variants(
            self.arguments_constructor_for_emptiness,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_rel_opt_variants_and_expectation_type_variants(
            self.arguments_constructor_for_emptiness,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )


class TestHardErrorWhenAFileThatIsNotARegularFileIsTested(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    file_content_assertion_variants = [
        sm_arg.Empty(),
        sm_arg.NumLines(int_condition(comparators.NE, 0)),
        sm_arg.Equals('expected'),
    ]

    def test_hard_error_when_there_is_a_single_file_that_is_not_a_regular_file(self):
        parser = sut.parser.Parser()
        name_of_checked_dir = 'checked-dir'
        relativity_root_conf = tr.DEFAULT_REL_OPT_CONFIG
        non_regular_files = [
            empty_dir('a-directory'),
            sym_link('sym-link', 'non-existing-target')
        ]

        for file_contents_assertion in self.file_content_assertion_variants:
            for quantifier in Quantifier:
                arguments_constructor = args.complete_arguments_constructor(
                    name_of_checked_dir,
                    FileQuantificationAssertionVariant(
                        quantifier,
                        file_contents_arg2(file_contents_assertion)))
                for expectation_type in ExpectationType:
                    arguments = arguments_constructor.apply(pfh_expectation_type_config(expectation_type),
                                                            relativity_root_conf)
                    for non_regular_file in non_regular_files:
                        with self.subTest(
                                quantifier=quantifier.name,
                                expectation_type=expectation_type.name,
                                arguments=arguments,
                                non_regular_file=non_regular_file.name):
                            instruction_check.check(
                                self,
                                parser,
                                remaining_source(arguments),
                                arrangement=
                                ArrangementPostAct(
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
                                    main_result=asrt_pfh.is_hard_error__with_arbitrary_message()
                                )
                            )


class TestExistsEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    exists__empty__arguments = args.complete_arguments_constructor(
        name_of_checked_dir,
        FileQuantificationAssertionVariant(
            Quantifier.EXISTS,
            file_contents_arg2(sm_arg.Empty()))
    )

    @property
    def instruction_checker(self) -> InstructionChecker:
        return InstructionChecker(self, sut.parser.Parser(), tr.ACCEPTED_REL_OPT_CONFIGURATIONS)

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            main_result_for_positive_expectation=PassOrFail.PASS,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
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
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestForAllEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    for_all__empty__arguments = args.complete_arguments_constructor(
        name_of_checked_dir,
        FileQuantificationAssertionVariant(
            Quantifier.ALL,
            file_contents_arg2(sm_arg.Empty()))
    )

    @property
    def instruction_checker(self) -> InstructionChecker:
        return InstructionChecker(self, sut.parser.Parser(), tr.ACCEPTED_REL_OPT_CONFIGURATIONS)

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
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
            rel_opt_config=tr.DEFAULT_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked(unittest.TestCase):
    file_content_assertion_variants_that_pass_iff_file_is_empty = [
        sm_arg.Empty(),
        sm_arg.NumLines(int_condition(comparators.EQ, 0)),
        sm_arg.Equals(shlex.quote('')),
    ]

    def test__all__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        parser = sut.parser.Parser()
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = NameAndValue(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            empty_file(
                'selected-empty-file.txt'),
            File(
                'un-selected-non-empty-file.txt', 'contents of non-emtpy file'),
            empty_dir(
                'un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = SymbolTable({
            name_starts_with_selected.name: container(FileMatcherConstantSdv(name_starts_with_selected.value))
        })
        relativity_root_conf = tr.DEFAULT_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for pass_iff_file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                name_of_checked_dir,
                FileQuantificationAssertionVariant(
                    Quantifier.ALL,
                    file_contents_arg2(pass_iff_file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = pfh_expectation_type_config(expectation_type)
                arguments = arguments_constructor.apply(etc,
                                                        relativity_root_conf)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    instruction_check.check(
                        self,
                        parser,
                        remaining_source(arguments),
                        arrangement=
                        ArrangementPostAct(
                            tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            main_result=etc.pass__if_positive__fail__if_negative,
                            symbol_usages=expected_symbol_references
                        )
                    )

    def test__exists__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        parser = sut.parser.Parser()
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = NameAndValue(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            File(
                'selected-non-empty-file.txt', 'contents of non-emtpy file'),
            empty_file(
                'un-selected-empty-file.txt'),
            empty_dir(
                'un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = SymbolTable({
            name_starts_with_selected.name: container(FileMatcherConstantSdv(name_starts_with_selected.value))
        })
        relativity_root_conf = tr.DEFAULT_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                name_of_checked_dir,
                FileQuantificationAssertionVariant(
                    Quantifier.EXISTS,
                    file_contents_arg2(file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = pfh_expectation_type_config(expectation_type)
                arguments = arguments_constructor.apply(etc,
                                                        relativity_root_conf)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    instruction_check.check(
                        self,
                        parser,
                        remaining_source(arguments),
                        arrangement=
                        ArrangementPostAct(
                            tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            main_result=etc.fail__if_positive__pass_if_negative,
                            symbol_usages=expected_symbol_references
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
    def instruction_checker(self) -> InstructionChecker:
        return InstructionChecker(self, sut.parser.Parser(), tr.ACCEPTED_REL_OPT_CONFIGURATIONS)

    def test_it_SHOULD_be_possible_to_create_multiple_intermediate_files(self):
        original_file_contents = 'original_file_contents'
        expected_transformer_contents = original_file_contents.upper()

        transform_to_uppercase = NameAndValue(
            'to_uppercase_lines_transformer',
            ToUppercaseStringTransformer())

        symbol_table_with_lines_transformer = SymbolTable({
            transform_to_uppercase.name: container(StringTransformerSdvConstant(transform_to_uppercase.value))
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(transform_to_uppercase.name)
        ])

        for_all__equals__arguments = args.complete_arguments_constructor(
            self.name_of_checked_dir,
            FileQuantificationAssertionVariant(
                Quantifier.ALL,
                file_contents_arg2(sm_arg.Transformed(transform_to_uppercase.name,
                                                      sm_arg.Equals(expected_transformer_contents)))
            ))
        relativity_root_conf = tr.DEFAULT_REL_OPT_CONFIG
        etc = pfh_expectation_type_config(ExpectationType.POSITIVE)
        arguments = for_all__equals__arguments.apply(
            etc,
            relativity_root_conf,
        )
        instruction_check.check(
            self,
            sut.parser.Parser(),
            remaining_source(arguments),
            arrangement=
            ArrangementPostAct(
                tcds_contents=relativity_root_conf.populator_for_relativity_option_root(
                    DirContents([
                        Dir(self.name_of_checked_dir, [
                            File('1.txt', original_file_contents),
                            File('2.txt', original_file_contents),
                        ])
                    ])
                ),
                symbols=symbol_table_with_lines_transformer
            ),
            expectation=
            Expectation(
                main_result=etc.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
