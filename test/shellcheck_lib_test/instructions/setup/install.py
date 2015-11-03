import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib.instructions.setup import install as sut
from shellcheck_lib_test.instructions.utils import new_source
from shellcheck_lib_test.util.file_structure import DirContents, File, Dir, empty_file, empty_dir
from shellcheck_lib_test.instructions.test_resources import eds_populator


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = utils.new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_two_arguments(self):
        source = utils.new_source('instruction-name', 'argument1 argument2 argument3')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = utils.new_source('instruction-name', 'single-argument')
        sut.Parser().apply(source)

    def test_succeed_when_there_is_exactly_two_arguments(self):
        source = utils.new_source('instruction-name', 'argument1 argument2')
        sut.Parser().apply(source)

    def test_argument_shall_be_parsed_using_shell_syntax(self):
        source = utils.new_source('instruction-name', "'argument 1' 'argument 2'")
        sut.Parser().apply(source)


class TestValidationErrorScenarios(TestCaseBase):
    def test_ERROR_when_file_does_not_exist__without_explicit_destination(self):
        self._check(
            Flow(sut.Parser(),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            utils.new_source('instruction-name',
                             'source-that-do-not-exist'))

    def test_ERROR_when_file_does_not_exist__with_explicit_destination(self):
        self._check(
            Flow(sut.Parser(),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            utils.new_source('instruction-name',
                             'source-that-do-not-exist destination'))


class TestSuccessfulScenarios(TestCaseBase):
    def test_install_file__without_explicit_destination(self):
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=file_to_install,
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     file_to_install)
                 ),
            new_source('instruction-name',
                       file_name))

    def test_install_file__with_explicit_destination__non_existing_file(self):
        src = 'src-file'
        dst = 'dst-file'
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([(File(src,
                                                      'contents'))]),
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     DirContents([(File(dst,
                                        'contents'))]))
                 ),
            new_source('instruction-name',
                       '{} {}'.format(src, dst)))

    def test_install_file__with_explicit_destination__existing_directory(self):
        src = 'src-file'
        dst = 'dst-dir'
        file_to_install = File(src, 'contents')
        home_dir_contents = [file_to_install]
        act_dir_contents = [empty_dir(dst)]
        act_dir_contents_after = [Dir(dst, [file_to_install])]
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents(home_dir_contents),
                 eds_contents_before_main=eds_populator.FilesInActDir(DirContents(act_dir_contents)),
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     DirContents(act_dir_contents_after))
                 ),
            new_source('instruction-name',
                       '{} {}'.format(src, dst)))

    def test_install_directory__without_explicit_destination(self):
        src_dir = 'existing-dir'
        files_to_install = DirContents([Dir(src_dir,
                                            [File('a', 'a'),
                                             Dir('d', []),
                                             Dir('d2',
                                                 [File('f', 'f')])
                                             ])])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=files_to_install,
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     files_to_install)
                 ),
            new_source('instruction-name',
                       src_dir))

    def test_install_directory__with_explicit_destination__existing_directory(self):
        src_dir = 'existing-dir'
        dst_dir = 'existing-dst-dir'
        files_to_install = [Dir(src_dir,
                                [File('a', 'a'),
                                 Dir('d', []),
                                 Dir('d2',
                                     [File('f', 'f')])
                                 ])]
        act_dir_contents_before = DirContents([empty_dir(dst_dir)])
        act_dir_contents_after = DirContents([Dir(dst_dir, files_to_install)])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents(files_to_install),
                 eds_contents_before_main=eds_populator.FilesInActDir(act_dir_contents_before),
                 expected_main_side_effects_on_files=eds_contents_check.ActRootContainsExactly(
                     act_dir_contents_after)
                 ),
            new_source('instruction-name',
                       '{} {}'.format(src_dir, dst_dir)))


class TestFailingScenarios(TestCaseBase):
    def test_destination_already_exists__without_explicit_destination(self):
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=file_to_install,
                 eds_contents_before_main=eds_populator.FilesInActDir(DirContents([empty_file(file_name)])),
                 expected_main_result=sh_check.IsHardError()
                 ),
            new_source('instruction-name',
                       file_name))

    def test_destination_already_exists__with_explicit_destination(self):
        src = 'src-file-name'
        dst = 'dst-file-name'
        home_dir_contents = DirContents([(empty_file(src))])
        act_dir_contents = DirContents([empty_file(dst)])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=home_dir_contents,
                 eds_contents_before_main=eds_populator.FilesInActDir(act_dir_contents),
                 expected_main_result=sh_check.IsHardError()
                 ),
            new_source('instruction-name',
                       '{} {}'.format(src, dst)))

    def test_destination_already_exists_in_destination_directory(self):
        src = 'src-file-name'
        dst = 'dst-dir-name'
        home_dir_contents = DirContents([(empty_file(src))])
        act_dir_contents = DirContents([Dir(dst,
                                            [empty_file(src)])])
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=home_dir_contents,
                 eds_contents_before_main=eds_populator.FilesInActDir(act_dir_contents),
                 expected_main_result=sh_check.IsHardError()
                 ),
            new_source('instruction-name',
                       '{} {}'.format(src, dst)))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestValidationErrorScenarios))
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
