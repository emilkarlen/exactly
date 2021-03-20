import unittest
from typing import Optional

from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.instructions.assert_ import existence_of_file as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType, RelSdsOptionType, \
    PathRelativityVariants, RelHdsOptionType
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.existence_of_file.test_resources import arguments_building as args
from exactly_lib_test.impls.instructions.assert_.existence_of_file.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.existence_of_file.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker, \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation2, \
    ExecutionExpectation, MultiSourceExpectation
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    with_negation_argument, PassOrFail, ExpectationTypeConfigForPfh
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration, \
    conf_rel_sds
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_action import MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.tcfs.test_resources.path_arguments import symbol_path_argument, \
    path_argument
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ArrangementPostAct2
from exactly_lib_test.test_resources.files.file_structure import DirContents, Link, \
    empty_dir_contents, File, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import TcdsActionFromPlainTcdsAction
from exactly_lib_test.test_resources.test_utils import NEA, NInpArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import references as fm_references
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.symbol_context import FileMatcherSymbolContext, \
    FileMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.validation_cases import \
    failing_validation_cases__svh
from exactly_lib_test.type_val_deps.types.path.test_resources.references import path_or_string_reference_restrictions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),
        SymbolUsagesTest(),
        FileMatcherValidationTest(),
        HardErrorInFileMatcherTest(),
        unittest.makeSuite(TestCheckForAnyTypeOfFile),
        unittest.makeSuite(TestCheckForRegularFile),
        unittest.makeSuite(TestCheckForDirectory),
        unittest.makeSuite(TestCheckForSymLink),
        unittest.makeSuite(TestDifferentSourceVariants),
        TestMatcherShouldBeParsedAsFullExpression(),
        TestNonExistingPathThatSpecifiesAFileInADirThatIsARegularFile(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParseInvalidSyntax(instruction_check.TestCaseBase):
    test_cases_with_no_negation_operator = [
        '',
        '{type_option} file-name'.format(
            type_option=option_syntax(OptionName(file_properties.TYPE_INFO[FileType.REGULAR].type_argument))),
        '{type_option}'.format(
            type_option=option_syntax(OptionName(file_properties.TYPE_INFO[FileType.DIRECTORY].type_argument))),
        '{invalid_option} file-name'.format(
            invalid_option=long_option_syntax('invalidOption')),
        'file-name unexpectedArgument',
    ]

    def test_raise_exception_WHEN_syntax_is_invalid(self):

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            self.test_cases_with_no_negation_operator)

    def test_raise_exception_WHEN_syntax_is_invalid_WITH_not_operator(self):

        test_cases_with_negation_operator = [
            with_negation_argument(case_with_no_negation_operator)
            for case_with_no_negation_operator in self.test_cases_with_no_negation_operator
        ]

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            test_cases_with_negation_operator)

    def _assert_each_case_raises_SingleInstructionInvalidArgumentException(self, test_cases: list):
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(instruction_argument=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestMatcherShouldBeParsedAsFullExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        checked_file = File.empty('the-checked-file.txt')

        fm_1 = FileMatcherSymbolContextOfPrimitiveConstant('fm_1', True)
        fm_2 = FileMatcherSymbolContextOfPrimitiveConstant('fm_2', False)
        symbols = [fm_1, fm_2]

        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT)

        arguments = args.CompleteInstructionArg(
            ExpectationType.POSITIVE,
            rel_conf.path_argument_of_rel_name(checked_file.name),
            fm_args.disjunction([fm_1.argument, fm_2.argument]),
        )
        is_pass = fm_1.result_value or fm_2.result_value
        # ACT # & ASSERT #
        CHECKER.check_2(
            self,
            arguments.as_remaining_source,
            ArrangementPostAct2(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds=TcdsArrangementPostAct(
                    tcds_contents=rel_conf.populator_for_relativity_option_root(
                        DirContents([checked_file])
                    )
                )
            ),
            Expectation2(
                ParseExpectation(
                    source=asrt_source.source_is_at_end,
                    symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols),
                ),
                ExecutionExpectation(
                    main_result=pfh_assertions.is_non_hard_error(is_pass),
                ),
            )
        )


class SymbolUsagesTest(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        path_symbol_name = 'the_path_symbol'
        file_matcher_symbol_name = 'the_file_matcher_symbol'

        expected_path_symbol_ref = asrt_sym_ref.symbol_usage_equals_data_type_symbol_reference(
            SymbolReference(path_symbol_name,
                            path_or_string_reference_restrictions(
                                EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS))
        )

        expected_file_matcher_ref = fm_references.is_reference_to_file_matcher(file_matcher_symbol_name)

        cases = [
            NEA('no symbols',
                asrt.matches_sequence([]),
                args.WithOptionalNegation(path_argument('plain-file-name'))
                ),
            NEA('path symbol',
                asrt.matches_sequence([
                    expected_path_symbol_ref,
                ]),
                args.WithOptionalNegation(symbol_path_argument(path_symbol_name))
                ),
            NEA('path symbol and file matcher symbol',
                asrt.matches_sequence([
                    expected_path_symbol_ref,
                    expected_file_matcher_ref,
                ]),
                args.WithOptionalNegation(symbol_path_argument(path_symbol_name),
                                          fm_args.SymbolReference(file_matcher_symbol_name))
                ),
        ]

        for case in cases:
            for expectation_type in ExpectationType:
                arguments = case.actual.get(expectation_type)
                source = remaining_source(str(arguments))
                with self.subTest(case=case.name,
                                  expectation_type=expectation_type):
                    # ACT #
                    instruction = sut.setup('the-instruction-name').parse(ARBITRARY_FS_LOCATION_INFO, source)
                    # ASSERT #
                    self.assertIsInstance(instruction, AssertPhaseInstruction)
                    case.expected.apply_without_message(self,
                                                        instruction.symbol_usages())


class FileMatcherValidationTest(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        for failing_file_matcher_case in failing_validation_cases__svh():
            failing_symbol_context = failing_file_matcher_case.value.symbol_context

            argument = args.CompleteInstructionArg(
                ExpectationType.POSITIVE,
                path_argument('ignored-file'),
                fm_args.SymbolReference(failing_symbol_context.name))

            with self.subTest(failing_file_matcher_case.name):
                # ACT & ASSERT #

                CHECKER.check(
                    self,
                    remaining_source(str(argument)),
                    ArrangementPostAct(
                        symbols=failing_symbol_context.symbol_table,
                    ),
                    instruction_check.expectation(
                        validation=failing_file_matcher_case.value.expectation,
                        symbol_usages=failing_symbol_context.references_assertion
                    ))


class HardErrorInFileMatcherTest(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        error_message = 'error message from file matcher'
        file_matcher_that_raises_hard_error = FileMatcherSymbolContext.of_primitive(
            'file_matcher_that_raises_hard_error',
            matchers.MatcherThatReportsHardError(error_message)
        )

        path_relativity = conf_rel_sds(RelSdsOptionType.REL_ACT)

        checked_file = File.empty('checked-file.txt')

        argument = args.CompleteInstructionArg(
            ExpectationType.POSITIVE,
            path_relativity.path_argument_of_rel_name(checked_file.name),
            fm_args.SymbolReference(file_matcher_that_raises_hard_error.name))

        # ACT & ASSERT #

        CHECKER.check(
            self,
            remaining_source(str(argument)),
            ArrangementPostAct(
                symbols=file_matcher_that_raises_hard_error.symbol_table,
                sds_contents=path_relativity.populator_for_relativity_option_root__sds(
                    DirContents([checked_file])
                )
            ),
            instruction_check.expectation(
                main_result=pfh_assertions.is_hard_error(
                    asrt_text_doc.rendered_text_matches(asrt_str.contains(error_message))
                ),
                symbol_usages=asrt.matches_sequence([
                    file_matcher_that_raises_hard_error.reference_assertion
                ])
            ))


class ArgumentsConstructorWithFileMatcher(InstructionArgumentsVariantConstructor):
    def __init__(self,
                 file_name: str,
                 file_matcher: Optional[fm_args.FileMatcherArg] = None):
        self._file_matcher = file_matcher
        self._file_name = file_name

    def apply(self,
              etc: ExpectationTypeConfigForPfh,
              rel_opt_config: RelativityOptionConfiguration) -> str:
        argument = args.CompleteInstructionArg(
            etc.expectation_type,
            rel_opt_config.path_argument_of_rel_name(self._file_name),
            self._file_matcher)

        return str(argument)


def arguments_constructor_for_file_type(file_name: str,
                                        file_type: FileType) -> InstructionArgumentsVariantConstructor:
    return ArgumentsConstructorWithFileMatcher(file_name, fm_args.Type(file_type))


class TestCaseBase(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.checker = InstructionChecker(
            self,
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )


class TestDifferentSourceVariants(TestCaseBase):
    def test_without_file_type(self):
        file_name = 'existing-file'
        instruction_argument_constructor = ArgumentsConstructorWithFileMatcher(file_name)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([File.empty(file_name)]),

        )

    def test_with_file_type(self):
        file_name = 'existing-file'
        instruction_argument_constructor = arguments_constructor_for_file_type(file_name, FileType.REGULAR)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([File.empty(file_name)]),

        )


class TestCheckForAnyTypeOfFile(TestCaseBase):
    def test_file_exists(self):
        # ARRANGE #
        file_name = 'existing-file'
        instruction_argument_constructor = ArgumentsConstructorWithFileMatcher(file_name)

        cases_with_existing_file_of_different_types = [
            NameAndValue(
                'dir',
                DirContents([Dir.empty(file_name)])),
            NameAndValue(
                'regular file',
                DirContents([File.empty(file_name)])),
            NameAndValue(
                'sym-link',
                DirContents(
                    [Dir.empty('directory'),
                     Link(file_name, 'directory')])
            ),
            NameAndValue(
                'broken sym-link',
                DirContents(
                    [Link(file_name, 'non-existing-target-file')])
            ),
        ]

        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            cases_with_existing_file_of_different_types,
            instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.PASS,
        )

    def test_file_does_not_exist(self):
        instruction_argument_constructor = ArgumentsConstructorWithFileMatcher('non-existing-file')

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL)


class TestCheckForDirectory(TestCaseBase):
    file_name = 'name-of-checked-file'
    instruction_argument_constructor = arguments_constructor_for_file_type(
        file_name,
        FileType.DIRECTORY)

    cases_with_existing_directory = [
        NameAndValue(
            'exists as directory',
            DirContents([Dir.empty(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing directory',
            DirContents([Dir.empty('directory'),
                         Link(file_name, 'directory')]),
        ),
    ]

    cases_with_existing_files_that_are_not_directories = [
        NameAndValue(
            'exists as regular file',
            DirContents([File.empty(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([File.empty('existing-file'),
                         Link(file_name, 'directory')]),
        ),
        NameAndValue(
            'broken sym-link',
            DirContents(
                [Link(file_name, 'non-existing-target-file')])
        ),
    ]

    cases_with_non_existing_files = [
        NameAndValue(
            'non-existing file',
            empty_dir_contents()
        ),
    ]

    def test_file_is_an_existing_directory(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_directory,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.PASS,
        )

    def test_file_exists_but_is_not_a_directory(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_files_that_are_not_directories,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )

    def test_file_does_not_exist(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_non_existing_files,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )


class TestCheckForRegularFile(TestCaseBase):
    file_name = 'name-of-checked-file'
    instruction_argument_constructor = arguments_constructor_for_file_type(
        file_name,
        FileType.REGULAR)

    cases_with_existing_files_that_are_regular_files = [
        NameAndValue(
            'exists as regular file',
            DirContents([File.empty(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([File.empty('existing-file'),
                         Link(file_name, 'existing-file')]),
        ),
    ]

    cases_with_existing_files_that_are_not_regular_files = [
        NameAndValue(
            'exists as directory',
            DirContents([Dir.empty(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing directory',
            DirContents([Dir.empty('directory'),
                         Link(file_name, 'directory')]),
        ),
        NameAndValue(
            'broken sym-link',
            DirContents(
                [Link(file_name, 'non-existing-target-file')])
        ),
    ]

    cases_with_non_existing_files = [
        NameAndValue(
            'non-existing file',
            empty_dir_contents()
        ),
    ]

    def test_file_exists_and_is_a_regular_file(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_files_that_are_regular_files,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.PASS,
        )

    def test_file_exists_but_is_not_a_regular_file(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_files_that_are_not_regular_files,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )

    def test_file_does_not_exist(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_non_existing_files,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )


class TestCheckForSymLink(TestCaseBase):
    file_name = 'the-name-of-checked-file'
    instruction_argument_constructor = arguments_constructor_for_file_type(
        file_name,
        FileType.SYMLINK)

    cases_with_existing_files_that_are_symbolic_links = [
        NameAndValue(
            'exists as sym-link to directory',
            DirContents([Dir.empty('dir'),
                         Link(file_name, 'dir')])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([File.empty('file'),
                         Link(file_name, 'file')]),
        ),
        NameAndValue(
            'exists as sym-link to non-existing file',
            DirContents([Link(file_name, 'non-existing-file')]),
        ),
    ]

    cases_with_existing_files_that_are_not_symbolic_links = [
        NameAndValue(
            'exists as directory',
            DirContents([File.empty(file_name)])
        ),
        NameAndValue(
            'exists as regular file',
            DirContents([Dir.empty(file_name)]),
        ),
    ]

    cases_with_non_existing_files = [
        NameAndValue(
            'non-existing file',
            empty_dir_contents()
        ),
    ]

    def test_file_exists_and_is_a_regular_file(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_files_that_are_symbolic_links,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.PASS,
        )

    def test_file_exists_but_is_not_a_regular_file(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_existing_files_that_are_not_symbolic_links,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )

    def test_file_does_not_exist(self):
        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self.cases_with_non_existing_files,
            self.instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL,
        )


class TestNonExistingPathThatSpecifiesAFileInADirThatIsARegularFile(unittest.TestCase):
    def runTest(self):
        file_in_root = File.empty('file-in-root.txt')
        files_in_root_dir = [file_in_root]

        file_matcher_symbol = FileMatcherSymbolContext.of_primitive_constant(
            'FILE_MATCHER_SYMBOL',
            True,
        )

        file_matcher_cases = [
            NInpArr(
                'wo file matcher',
                None,
                (),
            ),
            NInpArr(
                'w file matcher',
                file_matcher_symbol.abstract_syntax,
                [file_matcher_symbol],
            ),
        ]
        relativity_cases = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP),
            rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE),
        ]

        for expectation_type in ExpectationType:
            for file_matcher_case in file_matcher_cases:
                for rel_conf in relativity_cases:
                    with self.subTest(relativity=rel_conf.relativity,
                                      file_matcher=file_matcher_case.name,
                                      expectation_type=expectation_type):
                        CHECKER.check__abs_stx__source_variants(
                            self,
                            InstructionArguments(
                                rel_conf.path_abs_stx_of_name__c([
                                    file_in_root.name,
                                    'path-to-check'
                                ]),
                                expectation_type=expectation_type,
                                file_matcher=file_matcher_case.input,
                            ),
                            ArrangementPostAct2(
                                symbols=SymbolContext.symbol_table_of_contexts(file_matcher_case.arrangement),
                                tcds=TcdsArrangementPostAct(
                                    tcds_contents=rel_conf.populator_for_relativity_option_root(
                                        DirContents(files_in_root_dir)
                                    )
                                )
                            ),
                            MultiSourceExpectation(
                                symbol_usages=SymbolContext.usages_assertion_of_contexts(file_matcher_case.arrangement),
                                execution=ExecutionExpectation(
                                    main_result=pfh_assertions.is_pass_of_fail(
                                        expectation_type is ExpectationType.NEGATIVE
                                    )
                                )
                            )
                        )


EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {RelOptionType.REL_CWD,
     RelOptionType.REL_HDS_CASE,
     RelOptionType.REL_HDS_ACT,
     RelOptionType.REL_ACT,
     RelOptionType.REL_TMP},
    True)

ACCEPTED_REL_OPT_CONFIGURATIONS = (
        list(map(rel_opt_conf.conf_rel_any, EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS.rel_option_types)) +

        [rel_opt_conf.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                          'symbol_name',
                                          EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS)] +

        [rel_opt_conf.default_conf_rel_any(RelOptionType.REL_CWD)]
)

UNACCEPTED_REL_OPT_CONFIGURATIONS = [
    rel_opt_conf.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
    rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_RESULT),
]

MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = TcdsActionFromPlainTcdsAction(
    MkSubDirAndMakeItCurrentDirectory(
        SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd')
    )
)
if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
