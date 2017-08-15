import unittest

from exactly_lib.help_texts.file_ref import REL_symbol_OPTION
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils import parse_dir_contents_selector
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHomeOptionType, \
    PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_relativity
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources import expression
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, Expectation
from exactly_lib_test.instructions.assert_.test_resources.instruction_check_with_not_and_rel_opts import \
    InstructionChecker, InstructionArgumentsVariantConstructor
from exactly_lib_test.instructions.assert_.test_resources.instruction_with_negation_argument import \
    ExpectationTypeConfig, PassOrFail
from exactly_lib_test.instructions.assert_.utils import parse_dir_contents_selector as parse_test
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestTestCommonFailureConditionsForEmpty),
        unittest.makeSuite(TestEmpty),
        unittest.makeSuite(TestDifferentSourceVariantsForEmpty),
        unittest.makeSuite(TestEmptyWithFileSelector),

        unittest.makeSuite(TestTestCommonFailureConditionsForNumFiles),
        unittest.makeSuite(TestDifferentSourceVariantsForNumFiles),
        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgumentForNumFiles),
        unittest.makeSuite(TestFailingValidationPreSdsCausedByCustomValidationForNumFiles),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('the-instruction-name')),
    ])


class TheInstructionArgumentsVariantConstructorForNotAndRelOpt(InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given negation-option config
    and rel-opt config.
    """

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        ret_val = self.instruction_argument_template.replace('<rel_opt>', rel_opt_config.option_string)
        ret_val = etc.instruction_arguments(ret_val)
        return ret_val


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return 'ignored-name-of-dir-to-check {num_files} {condition}'.format(
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            condition=condition_str)


class TestCaseBaseForParser(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.checker = InstructionChecker(
            self,
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )


class TestParseInvalidSyntax(TestCaseBase):
    test_cases_with_no_negation_operator = [
        NameAndValue(
            'no arguments',
            '',
        ),
        NameAndValue(
            'valid file argument, but no operator',
            'file-name',
        ),
        NameAndValue(
            'valid file argument, invalid operator',
            'file-name invalid-operator',
        ),
        NameAndValue(
            'invalid option before file argument',
            '{invalid_option} file-name'.format(
                invalid_option=long_option_syntax('invalidOption'))
        ),
        NameAndValue(
            'missing argument for selector option ' + sut.SELECTION_OPTION.name.long,
            'file-name {selection_option} {empty}'.format(
                selection_option=option_syntax.option_syntax(parse_dir_contents_selector.SELECTION_OPTION.name),
                empty=sut.EMPTINESS_CHECK_ARGUMENT
            )
        ),
        NameAndValue(
            'missing argument for num-files option ' + sut.SELECTION_OPTION.name.long,
            'file-name {num_files}'.format(
                selection_option=option_syntax.option_syntax(parse_dir_contents_selector.SELECTION_OPTION.name),
                num_files=sut.NUM_FILES_CHECK_ARGUMENT
            )
        ),
        NameAndValue(
            'superfluous argument for num-files option ' + sut.SELECTION_OPTION.name.long,
            'file-name {num_files} {eq} 10 superfluous'.format(
                selection_option=option_syntax.option_syntax(parse_dir_contents_selector.SELECTION_OPTION.name),
                num_files=sut.NUM_FILES_CHECK_ARGUMENT,
                eq=comparators.EQ.name,
            )
        ),
    ]

    def test_raise_exception_WHEN_syntax_is_invalid(self):

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            self.test_cases_with_no_negation_operator)

    def test_raise_exception_WHEN_relativity_is_unaccepted(self):

        test_cases = [
            NameAndValue('relativity:' + rel_opt_config.option_string,
                         instruction_arguments_for_emptiness_check(rel_opt_config,
                                                                   'file-name')
                         )
            for rel_opt_config in UNACCEPTED_REL_OPT_CONFIGURATIONS
        ]

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(test_cases)

    def _assert_each_case_raises_SingleInstructionInvalidArgumentException(self, test_cases: list):
        parser = sut.Parser()
        for name_and_instruction_argument_str in test_cases:
            with self.subTest(case_name=name_and_instruction_argument_str.name):
                for source in equivalent_source_variants(self, name_and_instruction_argument_str.value):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)


class TestDifferentSourceVariantsForEmpty(TestCaseBaseForParser):
    def test_file_is_directory_that_is_empty(self):
        empty_directory = empty_dir('name-of-empty-dir')

        instruction_argument_constructor = argument_constructor_for_emptiness_check(empty_directory.name)

        contents_of_relativity_option_root = DirContents([empty_directory])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_a_directory_that_is_not_empty(self):
        non_empty_directory = Dir('name-of-non-empty-dir', [empty_file('file-in-dir')])

        instruction_argument_constructor = argument_constructor_for_emptiness_check(non_empty_directory.name)

        contents_of_relativity_option_root = DirContents([non_empty_directory])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_directory_with_files_but_none_that_matches_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file = empty_file('b')
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory,
                                                                                    name_option_pattern=pattern)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )


class TestCommonFailureConditionsBase:
    @property
    def _checker(self) -> InstructionChecker:
        return InstructionChecker(
            self._get_unittest_test_case(),
            sut.Parser(),
            ACCEPTED_REL_OPT_CONFIGURATIONS,
        )

    def _get_unittest_test_case(self) -> unittest.TestCase:
        raise NotImplementedError('abstract method')

    def _arguments_for_valid_syntax(
            self, path_to_check: str) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
        raise NotImplementedError('abstract method')

    def test_fail_WHEN_file_does_not_exist(self):
        instruction_argument_constructor = self._arguments_for_valid_syntax('name-of-non-existing-file')

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail())

    def test_fail_WHEN_file_does_exist_but_is_not_a_directory(self):
        name_of_regular_file = 'name-of-existing-regular-file'

        instruction_argument_constructor = self._arguments_for_valid_syntax(name_of_regular_file)

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=DirContents([empty_file(name_of_regular_file)]))

    def test_fail_WHEN_file_is_a_sym_link_to_a_non_existing_file(self):
        broken_sym_link = sym_link('broken-sym-link', 'non-existing-file')

        instruction_argument_constructor = self._arguments_for_valid_syntax(broken_sym_link.name)

        contents_of_relativity_option_root = DirContents([broken_sym_link])

        self._checker.check_rel_opt_variants_with_same_result_for_every_expectation_type(
            instruction_argument_constructor,
            asrt_pfh.is_fail(),
            contents_of_relativity_option_root=contents_of_relativity_option_root)


class TestTestCommonFailureConditionsForEmpty(TestCommonFailureConditionsBase, TestCaseBaseForParser):
    def _arguments_for_valid_syntax(self,
                                    path_to_check: str) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
        return argument_constructor_for_emptiness_check(path_to_check)

    def _get_unittest_test_case(self) -> unittest.TestCase:
        return self


class TestEmpty(TestCaseBaseForParser):
    def test_file_is_directory_that_is_empty(self):
        name_of_empty_directory = 'name-of-empty_directory'
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_empty_directory)

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory)])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_a_directory_that_is_not_empty(self):
        name_of_directory = 'name-of-empty_directory'
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory, [
            empty_file('existing-file-in-checked-dir')
        ])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_a_symbolic_link_to_an_empty_directory(self):
        name_of_empty_directory = 'name-of-empty_directory'
        name_of_symbolic_link = 'link-to-empty_directory'

        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_symbolic_link)

        contents_of_relativity_option_root = DirContents([empty_dir(name_of_empty_directory),
                                                          sym_link(name_of_symbolic_link,
                                                                   name_of_empty_directory)])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)


class TestEmptyWithFileSelector(TestCaseBaseForParser):
    def test_file_is_directory_that_contain_files_but_non_matching_given_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file = empty_file('b')
        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory,
                                                                                    name_option_pattern=pattern)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_directory_that_contain_files_but_non_matching_given_type_pattern(self):
        type_selector = FileType.DIRECTORY

        existing_file = empty_file('a-regular-file')

        name_of_directory = 'name-of-directory'

        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory,
                                                                                    type_selection=type_selector)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root)

    def test_file_is_directory_that_contain_files_with_names_that_matches_given_name_pattern(self):
        name_of_directory = 'name-of-directory'
        pattern = 'a*'
        existing_file_1 = empty_file('a1')
        existing_file_2 = empty_file('a2')

        instruction_argument_constructor = argument_constructor_for_emptiness_check(name_of_directory,
                                                                                    name_option_pattern=pattern)

        contents_of_relativity_option_root = DirContents([Dir(name_of_directory,
                                                              [existing_file_1,
                                                               existing_file_2])])

        self.checker.check_rel_opt_variants_and_expectation_type_variants(
            instruction_argument_constructor,
            PassOrFail.FAIL,
            contents_of_relativity_option_root=contents_of_relativity_option_root)


class TestFailingValidationPreSdsDueToInvalidIntegerArgumentForNumFiles(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.Parser(),
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck())


class TestFailingValidationPreSdsCausedByCustomValidationForNumFiles(TestCaseBase):
    def test_fail_WHEN_integer_operand_is_negative(self):
        cases = [
            -1,
            -2,
        ]
        for invalid_value in cases:
            arguments = 'ignored-file-name {num_files} {invalid_condition}'.format(
                num_files=sut.NUM_FILES_CHECK_ARGUMENT,
                invalid_condition=_int_condition(comparators.EQ, invalid_value))

            with self.subTest(invalid_value=invalid_value):
                self._check(
                    sut.Parser(),
                    remaining_source(arguments,
                                     ['following line']),
                    ArrangementPostAct(),
                    Expectation(
                        validation_pre_sds=svh_assertions.is_validation_error(),
                    ),
                )


class TestSymbolReferencesForNumFiles(unittest.TestCase):
    def test_both_symbols_from_path_and_comparison_SHOULD_be_reported(self):
        # ARRANGE #

        path_sym_ref = SymbolReference(
            'path_symbol_name',
            parse_relativity.reference_restrictions_for_path_symbol(
                sut.ACTUAL_RELATIVITY_CONFIGURATION.options.accepted_relativity_variants))

        operand_sym_ref = SymbolReference('operand_symbol_name',
                                          string_made_up_by_just_strings())

        argument = '{rel_sym_opt} {path_sym} file-name {num_files} {cmp_op} {operand_sym_ref}'.format(
            rel_sym_opt=REL_symbol_OPTION,
            path_sym=path_sym_ref.name,
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            cmp_op=comparators.EQ.name,
            operand_sym_ref=symbol_reference_syntax_for_name(operand_sym_ref.name))

        source = remaining_source(argument)

        # ACT #

        actual_instruction = sut.Parser().parse(source)

        assert isinstance(actual_instruction, AssertPhaseInstruction)

        actual_symbol_references = actual_instruction.symbol_usages()

        # ASSERT #

        expected_symbol_references = [
            path_sym_ref,
            operand_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestDifferentSourceVariantsForNumFiles(TestCaseBaseForParser):
    def test_file_is_directory_that_has_expected_number_of_files(self):
        directory_with_one_file = Dir('name-of-dir', [empty_file('a-file-in-checked-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            directory_with_one_file.name,
            _int_condition(comparators.EQ, 1))

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )

    def test_file_is_a_directory_that_has_unexpected_number_of_files(self):
        directory_with_one_file = Dir('name-of-non-empty-dir',
                                      [empty_file('file-in-dir')])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            directory_with_one_file.name,
            _int_condition(comparators.EQ, 2))

        contents_of_relativity_option_root = DirContents([directory_with_one_file])

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
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
                                     empty_file('a file'),
                                     empty_file('b file'),
                                 ])

        contents_of_relativity_option_root = DirContents([dir_with_two_files])

        instruction_argument_constructor = argument_constructor_for_num_files_check(
            dir_with_two_files.name,
            _int_condition(comparators.EQ, 1),
            name_option_pattern=pattern_that_matches_exactly_one_file)

        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=contents_of_relativity_option_root,
        )


class TestTestCommonFailureConditionsForNumFiles(TestCommonFailureConditionsBase, TestCaseBaseForParser):
    def _arguments_for_valid_syntax(self,
                                    path_to_check: str) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
        return argument_constructor_for_num_files_check(path_to_check,
                                                        _int_condition(comparators.EQ, 1))

    def _get_unittest_test_case(self) -> unittest.TestCase:
        return self


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    return '{relativity_option} {file_name} {emptiness_assertion_argument}'.format(
        relativity_option=rel_opt.option_string,
        file_name=file_name,
        emptiness_assertion_argument=EMPTINESS_CHECK_ARGUMENT)


def argument_constructor_for_emptiness_check(file_name: str,
                                             name_option_pattern: str = '',
                                             type_selection: FileType = None
                                             ) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
    selection = _selection_arguments(name_option_pattern,
                                     type_selection)

    return TheInstructionArgumentsVariantConstructorForNotAndRelOpt(
        '<rel_opt> {file_name} {selection} {empty}'.format(
            file_name=file_name,
            empty=EMPTINESS_CHECK_ARGUMENT,
            selection=selection
        )
    )


def argument_constructor_for_num_files_check(file_name: str,
                                             int_condition: str,
                                             name_option_pattern: str = '',
                                             type_selection: FileType = None
                                             ) -> TheInstructionArgumentsVariantConstructorForNotAndRelOpt:
    selection = _selection_arguments(name_option_pattern,
                                     type_selection)

    return TheInstructionArgumentsVariantConstructorForNotAndRelOpt(
        '<rel_opt> {file_name} {selection} {num_files} {num_files_condition}'.format(
            file_name=file_name,
            selection=selection,
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            num_files_condition=int_condition,

        )
    )


def _selection_arguments(name_option_pattern: str = '',
                         type_selection: FileType = None) -> str:
    ret_val = ''

    if name_option_pattern or type_selection:
        ret_val = option_syntax.option_syntax(parse_dir_contents_selector.SELECTION_OPTION.name)
        if name_option_pattern:
            ret_val = ret_val + ' ' + parse_test.name_selector_of(name_option_pattern)
        if type_selection:
            if name_option_pattern:
                ret_val = ret_val + ' ' + parse_dir_contents_selector.AND_OPERATOR
            ret_val = ret_val + ' ' + parse_test.type_selector_of(type_selection)

    return ret_val


def _int_condition(operator: comparators.ComparisonOperator,
                   value: int) -> str:
    return operator.name + ' ' + str(value)


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
