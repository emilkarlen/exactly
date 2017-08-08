import unittest

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
    Expectation, is_pass
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


class TestParseInvalidSyntax(TestCaseBase):
    def test_raise_exception_when_syntax_is_invalid(self):
        test_cases = [
            '',
            '{} file-name unexpected-argument'.format(long_option_syntax(sut.TYPE_NAME_DIRECTORY)),
            '{}'.format(long_option_syntax(sut.TYPE_NAME_DIRECTORY)),
            '{} file-name'.format(long_option_syntax('invalidOption')),
            'file-name unexpected-argument',
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
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


class TestCheckForAnyTypeOfFile(TestCaseBaseForParser):
    def test_pass_when_file_exists(self):
        file_name = 'existing-file'
        cases = [
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
        for file_type, dir_contents in cases:
            with self.subTest(msg=file_type):
                self._run(file_name,
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_ACT, dir_contents)),
                          is_pass(),
                          )

    def test_fail_when_file_does_not_exist(self):
        self._run('non-existing-file',
                  ArrangementPostAct(),
                  Expectation(
                      main_result=pfh_check.is_fail()),
                  )


class TestOfCurrentDirectoryIsNotActDir(TestCaseBaseForParser):
    def test_pass_when_file_exists(self):
        file_name = 'existing-file'
        cases = [
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
        change_dir_to_tmp_usr_dir = HomeAndSdsActionFromSdsAction(ChangeDirTo(lambda sds: sds.tmp.user_dir))
        for file_type, dir_contents in cases:
            with self.subTest(msg=file_type):
                self._run(file_name,
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_TMP, dir_contents),
                              pre_contents_population_action=change_dir_to_tmp_usr_dir),
                          is_pass(),
                          )


class TestCheckForDirectory(TestCaseBaseForParser):
    def test_pass(self):
        file_name = 'name-of-checked-file'
        cases = [
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
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_DIRECTORY),
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                       actual_dir_contents)),
                          is_pass(),
                          )

    def test_fail(self):
        file_name = 'the-name-of-checked-file'
        cases = [
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
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_DIRECTORY),
                          ArrangementPostAct(
                              sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                       actual_dir_contents)),
                          Expectation(
                              main_result=pfh_check.is_fail()),
                          )


class TestCheckForRegularFile(TestCaseBaseForParser):
    def test_pass(self):
        file_name = 'name-of-checked-file'
        cases = [
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
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_REGULAR),
                          ArrangementPostAct(sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                                      actual_dir_contents)),
                          is_pass(),
                          )

    def test_fail(self):
        file_name = 'the-name-of-checked-file'
        cases = [
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
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_REGULAR),
                          ArrangementPostAct(sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                                      actual_dir_contents)),
                          Expectation(main_result=pfh_check.is_fail()),
                          )


class TestCheckForSymLink(TestCaseBaseForParser):
    def test_pass(self):
        file_name = 'name-of-checked-file'
        cases = [
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
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_SYMLINK),
                          ArrangementPostAct(sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                                      actual_dir_contents)),
                          is_pass(),
                          )

    def test_fail(self):
        file_name = 'the-name-of-checked-file'
        cases = [
            (
                'exists as directory',
                DirContents([empty_file(file_name)])
            ),
            (
                'exists as regular file',
                DirContents([empty_dir(file_name)]),
            ),
        ]
        for case_name, actual_dir_contents in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   file_type=sut.TYPE_NAME_SYMLINK),
                          ArrangementPostAct(sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                                                      actual_dir_contents)),
                          Expectation(main_result=pfh_check.is_fail()),
                          )


class TestFileRefVariantsOfCheckedFile(TestCaseBaseForParser):
    def test_pass(self):
        file_name = 'name-of-checked-file'
        cases = [
            (
                'exists in act dir',
                sut.TYPE_NAME_REGULAR,
                file_ref_texts.REL_ACT_OPTION,
                ArrangementPostAct(
                    sds_contents=contents_in(RelSdsOptionType.REL_ACT,
                                             DirContents([empty_file(file_name)]))),
                Expectation(symbol_usages=asrt.is_empty_list),
            ),
            (
                'exists in tmp/usr dir',
                sut.TYPE_NAME_DIRECTORY,
                file_ref_texts.REL_TMP_OPTION,
                ArrangementPostAct(
                    sds_contents=contents_in(RelSdsOptionType.REL_TMP,
                                             DirContents([empty_dir(file_name)]))),
                Expectation(symbol_usages=asrt.is_empty_list),
            ),
            (
                'exists in tmp/usr dir',
                sut.TYPE_NAME_DIRECTORY,
                file_ref_texts.REL_TMP_OPTION,
                ArrangementPostAct(
                    sds_contents=contents_in(RelSdsOptionType.REL_TMP,
                                             DirContents([empty_dir(file_name)]))),
                Expectation(symbol_usages=asrt.is_empty_list),
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
                Expectation(symbol_usages=asrt.matches_sequence([
                    equals_symbol_reference_with_restriction_on_direct_target(
                        'SYMBOL_NAME',
                        equals_file_ref_relativity_restriction(
                            FileRefRelativityRestriction(
                                sut._REL_OPTION_CONFIG.options.accepted_relativity_variants)
                        ))
                ])),
            ),
        ]
        for case_name, expected_file_type, relativity_option, arrangement, expectation in cases:
            with self.subTest(msg=case_name):
                self._run(args_for(file_name=file_name,
                                   relativity_option=relativity_option,
                                   file_type=expected_file_type),
                          arrangement,
                          expectation,
                          )


def args_for(file_name: str,
             file_type: str,
             relativity_option: str = '') -> str:
    return long_option_syntax(file_type) + ' ' + relativity_option + ' ' + file_name


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
