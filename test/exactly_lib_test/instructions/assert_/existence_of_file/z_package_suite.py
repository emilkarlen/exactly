import unittest
from typing import Optional

from exactly_lib.instructions.assert_ import existence_of_file as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType, \
    PathRelativityVariants, RelHomeOptionType
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.instructions.assert_.existence_of_file import test_resources as args
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionChecker, \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import file_matcher as asrt_file_matcher
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_resolvers
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import symbol_file_ref_argument, \
    file_ref_argument
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources.validation_cases import failing_validation_cases__svh
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    with_negation_argument, PassOrFail, ExpectationTypeConfigForPfh
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration, \
    conf_rel_sds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir, Link, \
    empty_dir_contents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.type_system.logic.test_resources.file_matchers import FileMatcherThatReportsHardError


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


class SymbolUsagesTest(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        path_symbol_name = 'the_path_symbol'
        file_matcher_symbol_name = 'the_file_matcher_symbol'

        expected_path_symbol_ref = asrt_sym_ref.symbol_usage_equals_symbol_reference(
            SymbolReference(path_symbol_name,
                            file_ref_or_string_reference_restrictions(
                                EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS))
        )

        expected_file_matcher_ref = asrt_file_matcher.is_file_matcher_reference_to__ref(file_matcher_symbol_name)

        cases = [
            NEA('no symbols',
                asrt.matches_sequence([]),
                args.WithOptionalNegation(args.PathArg(file_ref_argument('plain-file-name')))
                ),
            NEA('path symbol',
                asrt.matches_sequence([
                    expected_path_symbol_ref,
                ]),
                args.WithOptionalNegation(args.PathArg(symbol_file_ref_argument(path_symbol_name)))
                ),
            NEA('path symbol and file matcher symbol',
                asrt.matches_sequence([
                    expected_path_symbol_ref,
                    expected_file_matcher_ref,
                ]),
                args.WithOptionalNegation(args.PathArg(symbol_file_ref_argument(path_symbol_name)),
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
                args.PathArg(file_ref_argument('ignored-file')),
                fm_args.SymbolReference(failing_symbol_context.name))

            with self.subTest(failing_file_matcher_case.name):
                # ACT & ASSERT #

                instruction_check.check(
                    self,
                    sut.Parser(),
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
        file_matcher_that_raises_hard_error = NameAndValue(
            'file_matcher_that_raises_hard_error',
            self._resolver_of_matcher_that_causes_hard_error(error_message)
        )

        path_relativity = conf_rel_sds(RelSdsOptionType.REL_ACT)

        checked_file = empty_file('checked-file.txt')

        argument = args.CompleteInstructionArg(
            ExpectationType.POSITIVE,
            args.PathArg(path_relativity.file_argument_with_option(checked_file.name)),
            fm_args.SymbolReference(file_matcher_that_raises_hard_error.name))

        # ACT & ASSERT #

        instruction_check.check(
            self,
            sut.Parser(),
            remaining_source(str(argument)),
            ArrangementPostAct(
                symbols=symbol_table_from_name_and_resolvers([
                    file_matcher_that_raises_hard_error
                ]),
                sds_contents=path_relativity.populator_for_relativity_option_root__sds(
                    DirContents([checked_file])
                )
            ),
            instruction_check.expectation(
                main_result=pfh_assertions.is_hard_error(
                    asrt_text_doc.rendered_text_matches(asrt_str.contains(error_message))
                ),
                symbol_usages=asrt.matches_sequence([
                    asrt_file_matcher.is_file_matcher_reference_to__ref(file_matcher_that_raises_hard_error.name)
                ])
            ))

    @staticmethod
    def _resolver_of_matcher_that_causes_hard_error(err_msg: str) -> FileMatcherResolver:
        return FileMatcherConstantResolver(FileMatcherThatReportsHardError(err_msg))


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
            args.PathArg(rel_opt_config.file_argument_with_option(self._file_name)),
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
            contents_of_relativity_option_root=DirContents([empty_file(file_name)]),

        )

    def test_with_file_type(self):
        file_name = 'existing-file'
        instruction_argument_constructor = arguments_constructor_for_file_type(file_name, FileType.REGULAR)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([empty_file(file_name)]),

        )


class TestCheckForAnyTypeOfFile(TestCaseBase):
    def test_file_exists(self):
        # ARRANGE #
        file_name = 'existing-file'
        instruction_argument_constructor = ArgumentsConstructorWithFileMatcher(file_name)

        cases_with_existing_file_of_different_types = [
            NameAndValue(
                'dir',
                DirContents([empty_dir(file_name)])),
            NameAndValue(
                'regular file',
                DirContents([empty_file(file_name)])),
            NameAndValue(
                'sym-link',
                DirContents(
                    [empty_dir('directory'),
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
            DirContents([empty_dir(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing directory',
            DirContents([empty_dir('directory'),
                         Link(file_name, 'directory')]),
        ),
    ]

    cases_with_existing_files_that_are_not_directories = [
        NameAndValue(
            'exists as regular file',
            DirContents([empty_file(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([empty_file('existing-file'),
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
            DirContents([empty_file(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([empty_file('existing-file'),
                         Link(file_name, 'existing-file')]),
        ),
    ]

    cases_with_existing_files_that_are_not_regular_files = [
        NameAndValue(
            'exists as directory',
            DirContents([empty_dir(file_name)])
        ),
        NameAndValue(
            'exists as sym-link to existing directory',
            DirContents([empty_dir('directory'),
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
            DirContents([empty_dir('dir'),
                         Link(file_name, 'dir')])
        ),
        NameAndValue(
            'exists as sym-link to existing regular file',
            DirContents([empty_file('file'),
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
            DirContents([empty_file(file_name)])
        ),
        NameAndValue(
            'exists as regular file',
            DirContents([empty_dir(file_name)]),
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


EXPECTED_ACCEPTED_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {RelOptionType.REL_CWD,
     RelOptionType.REL_HOME_ACT,
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
    rel_opt_conf.conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
    rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_RESULT),
]

MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
