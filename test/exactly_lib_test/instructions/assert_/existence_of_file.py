import unittest
from enum import Enum

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.instructions.assert_ import existence_of_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsNothing
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, \
    Expectation
from exactly_lib_test.instructions.multi_phase_instructions.change_dir import ChangeDirTo
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants
from exactly_lib_test.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_with_single_file_ref_value
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_case_utils.parse.test_resources import rel_symbol_arg_str
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Link
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsActionFromSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),
        unittest.makeSuite(TestCheckForRegularFile),
        unittest.makeSuite(TestCheckForDirectory),
        unittest.makeSuite(TestCheckForSymLink),
        unittest.makeSuite(TestCheckForAnyTypeOfFile),
        unittest.makeSuite(TestOfCurrentDirectoryIsNotActDir),
        unittest.makeSuite(TestFileRefVariantsOfCheckedFile),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class CheckType(Enum):
    POSITIVE = 0
    NEGATIVE = 1


class TestParseInvalidSyntax(TestCaseBase):
    test_cases_with_no_negation_operator = [
        '',
        '{type_option} file-name unexpected-argument'.format(
            type_option=long_option_syntax(sut.TYPE_NAME_DIRECTORY)),
        '{type_option}'.format(
            type_option=long_option_syntax(sut.TYPE_NAME_DIRECTORY)),
        '{invalid_option} file-name'.format(
            invalid_option=long_option_syntax('invalidOption')),
        'file-name unexpected-argument',
    ]

    def test_raise_exception_WHEN_syntax_is_invalid(self):

        self._assert_each_case_raises_SingleInstructionInvalidArgumentException(
            self.test_cases_with_no_negation_operator)

    def test_raise_exception_WHEN_syntax_is_invalid_WITH_not_operator(self):

        test_cases_with_negation_operator = [
            sut.NEGATION_OPERATOR + ' ' + case_with_no_negation_operator
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
                        parser.parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             instruction_argument: str,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        parser = sut.Parser()
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._check(parser, source, arrangement, expectation)

    def _run_test_cases_with_act_dir_contents(self,
                                              test_cases_with_name_and_dir_contents: list,
                                              instruction_arguments: str,
                                              main_result: asrt.ValueAssertion):
        for case_name, actual_dir_contents in test_cases_with_name_and_dir_contents:
            with self.subTest(case_name=case_name,
                              arguments=instruction_arguments):
                self._run(instruction_arguments,
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                       actual_dir_contents)),
                          Expectation(
                              main_result=main_result),
                          )


class TestCheckForAnyTypeOfFile(TestCaseBaseForParser):
    file_name = 'existing-file'

    cases_with_existing_file_of_different_types = [
        ('dir',
         DirContents([empty_dir(file_name)])),
        ('regular file',
         DirContents([empty_file(file_name)])),
        ('sym-link',
         DirContents(
             [empty_dir('directory'),
              Link(file_name, 'directory')])
         ),
    ]

    def test_pass_WHEN_file_exists(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_file_of_different_types,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name),
        )

    def test_fail_WHEN_file_does_not_exist(self):
        self._run('non-existing-file',
                  ArrangementPostAct(),
                  Expectation(
                      main_result=pfh_check.is_fail()),
                  )

    def test_fail_WHEN_file_exists_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_file_of_different_types,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           check_type=CheckType.NEGATIVE),
        )

    def test_pass_WHEN_file_does_not_exist_AND_assertion_is_negated(self):
        self._run(with_negation_argument('non-existing-file'),
                  ArrangementPostAct(),
                  Expectation(
                      main_result=pfh_check.is_pass()),
                  )


class TestOfCurrentDirectoryIsNotActDir(TestCaseBaseForParser):
    name_of_existing_file = 'existing-file'
    cases_with_existing_file_of_different_type = [
        ('dir',
         DirContents([empty_dir(name_of_existing_file)])),
        ('regular file',
         DirContents([empty_file(name_of_existing_file)])),
        ('sym-link',
         DirContents(
             [empty_dir('directory'),
              Link(name_of_existing_file, 'directory')])
         ),
    ]

    def test_pass_WHEN_file_exists(self):
        change_dir_to_tmp_usr_dir = HomeAndSdsActionFromSdsAction(ChangeDirTo(lambda sds: sds.tmp.user_dir))
        for case_name, dir_contents in self.cases_with_existing_file_of_different_type:
            with self.subTest(case_name=case_name):
                self._run(self.name_of_existing_file,
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_TMP, dir_contents),
                              pre_contents_population_action=change_dir_to_tmp_usr_dir),
                          Expectation(
                              main_result=pfh_check.is_pass(),
                          ),
                          )

    def test_fail_WHEN_file_exists_AND_assertion_is_negated(self):
        change_dir_to_tmp_usr_dir = HomeAndSdsActionFromSdsAction(ChangeDirTo(lambda sds: sds.tmp.user_dir))
        for case_name, dir_contents in self.cases_with_existing_file_of_different_type:
            with self.subTest(case_name=case_name):
                self._run(with_negation_argument(self.name_of_existing_file),
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_TMP, dir_contents),
                              pre_contents_population_action=change_dir_to_tmp_usr_dir),
                          Expectation(
                              main_result=pfh_check.is_fail(),
                          ),
                          )


class TestCheckForDirectory(TestCaseBaseForParser):
    file_name = 'name-of-checked-file'

    cases_with_existing_directory = [
        (
            'exists as directory',
            DirContents([empty_dir(file_name)])
        ),
        (
            'exists as sym-link to existing directory',
            DirContents([empty_dir('directory'),
                         Link(file_name, 'directory')]),
        ),
    ]

    cases_with_existing_files_that_are_not_directories = [
        (
            'exists as regular file',
            DirContents([empty_file(file_name)])
        ),
        (
            'exists as sym-link to existing regular file',
            DirContents([empty_file('existing-file'),
                         Link(file_name, 'directory')]),
        ),
    ]

    def test_pass_WHEN_file_is_an_existing_directory(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_directory,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_DIRECTORY),
        )

    def test_fail_WHEN_file_exists_but_is_not_a_directory(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_directories,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_DIRECTORY),
        )

    def test_fail_WHEN_file_is_an_existing_directory_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_directory,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_DIRECTORY,
                                           check_type=CheckType.NEGATIVE),
        )

    def test_pass_WHEN_file_exists_but_is_not_a_directory_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_directories,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_DIRECTORY,
                                           check_type=CheckType.NEGATIVE),
        )


class TestCheckForRegularFile(TestCaseBaseForParser):
    file_name = 'name-of-checked-file'
    cases_with_existing_files_that_are_regular_files = [
        (
            'exists as regular file',
            DirContents([empty_file(file_name)])
        ),
        (
            'exists as sym-link to existing regular file',
            DirContents([empty_file('existing-file'),
                         Link(file_name, 'existing-file')]),
        ),
    ]

    cases_with_existing_files_that_are_not_regular_files = [
        (
            'exists as directory',
            DirContents([empty_dir(file_name)])
        ),
        (
            'exists as sym-link to existing directory',
            DirContents([empty_dir('directory'),
                         Link(file_name, 'directory')]),
        ),
    ]

    def test_pass_WHEN_file_exists_and_is_a_regular_file(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_regular_files,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_REGULAR),
        )

    def test_fail_WHE_file_exists_but_is_not_a_regular_file(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_regular_files,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_REGULAR),
        )

    def test_fail_WHEN_file_exists_and_is_a_regular_file_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_regular_files,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_REGULAR,
                                           check_type=CheckType.NEGATIVE),
        )

    def test_pass_WHE_file_exists_but_is_not_a_regular_file_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_regular_files,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_REGULAR,
                                           check_type=CheckType.NEGATIVE),
        )


class TestCheckForSymLink(TestCaseBaseForParser):
    file_name = 'the-name-of-checked-file'
    cases_with_existing_files_that_are_symbolic_links = [
        (
            'exists as sym-link to directory',
            DirContents([empty_dir('dir'),
                         Link(file_name, 'dir')])
        ),
        (
            'exists as sym-link to existing regular file',
            DirContents([empty_file('file'),
                         Link(file_name, 'file')]),
        ),
        (
            'exists as sym-link to non-existing file',
            DirContents([Link(file_name, 'non-existing-file')]),
        ),
    ]

    cases_with_existing_files_that_are_not_symbolic_links = [
        (
            'exists as directory',
            DirContents([empty_file(file_name)])
        ),
        (
            'exists as regular file',
            DirContents([empty_dir(file_name)]),
        ),
    ]

    def test_pass_WHEN_file_exists_and_is_a_regular_file(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_symbolic_links,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_SYMLINK),
        )

    def test_fail_file_exists_but_is_not_a_regular_file(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_symbolic_links,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_SYMLINK),
        )

    def test_fail_WHEN_file_exists_and_is_a_regular_file_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_symbolic_links,
            main_result=pfh_check.is_fail(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_SYMLINK,
                                           check_type=CheckType.NEGATIVE),
        )

    def test_pass_file_exists_but_is_not_a_regular_file_AND_assertion_is_negated(self):
        self._run_test_cases_with_act_dir_contents(
            self.cases_with_existing_files_that_are_not_symbolic_links,
            main_result=pfh_check.is_pass(),
            instruction_arguments=args_for(file_name=self.file_name,
                                           file_type=sut.TYPE_NAME_SYMLINK,
                                           check_type=CheckType.NEGATIVE),
        )


class TestFileRefVariantsOfCheckedFile(TestCaseBaseForParser):
    file_name = 'name-of-checked-file'
    cases = [
        (
            'exists in act dir',
            sut.TYPE_NAME_REGULAR,
            file_ref_texts.REL_ACT_OPTION,
            ArrangementPostAct(
                sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                         DirContents([empty_file(file_name)]))),
            asrt.is_empty_list,
        ),
        (
            'exists in tmp/usr dir',
            sut.TYPE_NAME_DIRECTORY,
            file_ref_texts.REL_TMP_OPTION,
            ArrangementPostAct(
                sds_contents=contents_in(RelSdsOptionType.REL_TMP,
                                         DirContents([empty_dir(file_name)]))),
            asrt.is_empty_list,
        ),
        (
            'exists relative symbol',
            sut.TYPE_NAME_DIRECTORY,
            rel_symbol_arg_str('SYMBOL_NAME'),
            ArrangementPostAct(
                symbols=symbol_table_with_single_file_ref_value(
                    'SYMBOL_NAME',
                    file_refs.of_rel_option(RelOptionType.REL_TMP,
                                            PathPartAsNothing())),
                sds_contents=contents_in(RelSdsOptionType.REL_TMP,
                                         DirContents([empty_dir(file_name)]))),
            asrt.matches_sequence([
                equals_symbol_reference_with_restriction_on_direct_target(
                    'SYMBOL_NAME',
                    equals_file_ref_relativity_restriction(
                        FileRefRelativityRestriction(
                            sut._REL_OPTION_CONFIG.options.accepted_relativity_variants)
                    ))
            ]),
        ),
    ]

    def test_pass(self):
        for case_name, expected_file_type, relativity_option, arrangement, expected_symbol_usages in self.cases:
            with self.subTest(case_name=case_name):
                self._run(args_for(file_name=self.file_name,
                                   relativity_option=relativity_option,
                                   file_type=expected_file_type),
                          arrangement,
                          Expectation(
                              main_result=pfh_check.is_pass(),
                              symbol_usages=expected_symbol_usages,
                          ),
                          )

    def test_fail_WHEN_assertion_is_negated(self):
        for case_name, expected_file_type, relativity_option, arrangement, expected_symbol_usages in self.cases:
            with self.subTest(case_name=case_name):
                self._run(args_for(file_name=self.file_name,
                                   relativity_option=relativity_option,
                                   file_type=expected_file_type,
                                   check_type=CheckType.NEGATIVE),
                          arrangement,
                          Expectation(
                              main_result=pfh_check.is_fail(),
                              symbol_usages=expected_symbol_usages,
                          ),
                          )


def with_negation_argument(instruction_arguments: str) -> str:
    return sut.NEGATION_OPERATOR + ' ' + instruction_arguments


def args_for(file_name: str,
             file_type: str = None,
             check_type: CheckType = CheckType.POSITIVE,
             relativity_option: str = '') -> str:
    file_type_option = '' if file_type is None else long_option_syntax(file_type)
    arguments = file_type_option + ' ' + relativity_option + ' ' + file_name
    if check_type is CheckType.NEGATIVE:
        arguments = with_negation_argument(arguments)
    return arguments


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
