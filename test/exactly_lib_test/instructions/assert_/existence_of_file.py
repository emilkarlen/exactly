import unittest

from exactly_lib.instructions.assert_ import existence_of_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, \
    arrangement, Expectation, is_pass
from exactly_lib_test.instructions.multi_phase_instructions.change_dir import ChangeDirTo
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import act_dir_contents, \
    tmp_user_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Link
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsActionFromSdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),
        unittest.makeSuite(TestCheckForRegularFile),
        unittest.makeSuite(TestCheckForDirectory),
        unittest.makeSuite(TestCheckForSymLink),
        unittest.makeSuite(TestCheckForAnyTypeOfFile),
        unittest.makeSuite(TestOfCurrentDirectoryIsNotActDir),
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
                          arrangement(sds_contents_before_main=act_dir_contents(dir_contents)),
                          is_pass(),
                          )

    def test_fail_when_file_does_not_exist(self):
        self._run('non-existing-file',
                  arrangement(),
                  Expectation(main_result=pfh_check.is_fail()),
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
                          arrangement(sds_contents_before_main=tmp_user_dir_contents(dir_contents),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
                          Expectation(main_result=pfh_check.is_fail()),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
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
                          arrangement(sds_contents_before_main=act_dir_contents(actual_dir_contents)),
                          Expectation(main_result=pfh_check.is_fail()),
                          )


def args_for(file_name: str, file_type: str) -> str:
    return long_option_syntax(file_type) + ' ' + file_name


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
