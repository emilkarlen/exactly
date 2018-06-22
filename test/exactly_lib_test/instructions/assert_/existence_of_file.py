import pathlib
import unittest

from exactly_lib.instructions.assert_ import existence_of_file as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType, \
    PathRelativityVariants, RelHomeOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, option_syntax
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionArgumentsVariantConstructorWithTemplateStringBase, InstructionChecker
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    with_negation_argument, PassOrFail, ExpectationTypeConfig
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir, Link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),
        unittest.makeSuite(TestCheckForRegularFile),
        unittest.makeSuite(TestCheckForDirectory),
        unittest.makeSuite(TestCheckForSymLink),
        unittest.makeSuite(TestCheckForAnyTypeOfFile),
        unittest.makeSuite(TestDifferentSourceVariants),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


FILE_TYPE_OPTIONS_DICT = dict(sut.FILE_TYPE_OPTIONS)

THE_FS_LOCATION_INFO = FileSystemLocationInfo(pathlib.Path.cwd())


def file_type_option(file_type: FileType) -> str:
    return '' if file_type is None else long_option_syntax(FILE_TYPE_OPTIONS_DICT[file_type].long)


class TestParseInvalidSyntax(instruction_check.TestCaseBase):
    test_cases_with_no_negation_operator = [
        '',
        '{type_option} file-name unexpected-argument'.format(
            type_option=option_syntax(FILE_TYPE_OPTIONS_DICT[FileType.DIRECTORY])),
        '{type_option}'.format(
            type_option=option_syntax(FILE_TYPE_OPTIONS_DICT[FileType.DIRECTORY])),
        '{invalid_option} file-name'.format(
            invalid_option=long_option_syntax('invalidOption')),
        'file-name unexpected-argument',
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
                        parser.parse(THE_FS_LOCATION_INFO, source)


class TheInstructionArgumentsVariantConstructor(InstructionArgumentsVariantConstructorWithTemplateStringBase):
    """
    Constructs the instruction argument for a given negation-option config
    and rel-opt config.
    """

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        ret_val = self.instruction_argument_template.replace('<rel_opt>', str(rel_opt_config.option_argument))
        ret_val = etc.instruction_arguments(ret_val)
        return ret_val


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
        instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
            '<rel_opt> {file_name}'.format(file_name=file_name)
        )
        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([empty_file(file_name)]),

        )

    def test_with_file_type(self):
        file_name = 'existing-file'
        instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
            '{file_type_opt} <rel_opt> {file_name}'.format(
                file_type_opt=file_type_option(FileType.REGULAR),
                file_name=file_name)
        )
        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([empty_file(file_name)]),

        )


class TestCheckForAnyTypeOfFile(TestCaseBase):
    def test_file_exists(self):
        file_name = 'existing-file'
        instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
            '<rel_opt> {file_name}'.format(file_name=file_name)
        )

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
        ]

        self.checker.check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            cases_with_existing_file_of_different_types,
            instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.PASS,
        )

    def test_file_does_not_exist(self):
        instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
            '<rel_opt> non-existing-file'
        )
        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            main_result_for_positive_expectation=PassOrFail.FAIL)


class TestCheckForDirectory(TestCaseBase):
    file_name = 'name-of-checked-file'
    instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
        '{file_type_opt} <rel_opt> {file_name}'.format(
            file_type_opt=file_type_option(FileType.DIRECTORY),
            file_name=file_name),
    )

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


class TestCheckForRegularFile(TestCaseBase):
    file_name = 'name-of-checked-file'
    instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
        '{file_type_opt} <rel_opt> {file_name}'.format(
            file_type_opt=file_type_option(FileType.REGULAR),
            file_name=file_name),
    )

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


class TestCheckForSymLink(TestCaseBase):
    file_name = 'the-name-of-checked-file'
    instruction_argument_constructor = TheInstructionArgumentsVariantConstructor(
        '{file_type_opt} <rel_opt> {file_name}'.format(
            file_type_opt=file_type_option(FileType.SYMLINK),
            file_name=file_name),
    )
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
