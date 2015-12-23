import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.assert_phase import type as sut
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir, Link


class TestParse(TestCaseBase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._check(
                Flow(sut.Parser()),
                new_source('instruction-name',
                           ''))

    def test_that_when_too_many_arguments_then_exception_is_raised(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._check(
                Flow(sut.Parser()),
                new_source('instruction-name',
                           'file-name file extra-argument'))


class TestCheckForDirectory(TestCaseBase):
    def test_pass__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir(file_name)]))),
            new_source('instruction-name',
                       file_name + ' directory'))

    def test_fail__when__actual_type_is_regular_file(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file(file_name)]))),
            new_source('instruction-name',
                       file_name + ' directory'))

    def test_pass__when__actual_type_is_sym_link_to_directory(self):
        file_name = 'sym-link'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir('directory'),
                      Link(file_name, 'directory')]))),
            new_source('instruction-name',
                       file_name + ' directory'))

    def test_fail__when__actual_type_is_sym_link_to_file(self):
        file_name = 'sym-link'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file('existing-file'),
                      Link(file_name, 'existing-file')]))),
            new_source('instruction-name',
                       file_name + ' directory'))


class TestCheckForRegularFile(TestCaseBase):
    def test_pass__when__actual_type_is_regular_file(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file(file_name)]))),
            new_source('instruction-name',
                       file_name + ' regular'))

    def test_fail__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir(file_name)]))),
            new_source('instruction-name',
                       file_name + ' regular'))

    def test_fail__when__actual_type_is_sym_link_to_directory(self):
        file_name = 'sym-link'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir('directory'),
                      Link(file_name, 'directory')]))),
            new_source('instruction-name',
                       file_name + ' regular'))

    def test_pass__when__actual_type_is_sym_link_to_file(self):
        file_name = 'sym-link'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file('existing-file'),
                      Link(file_name, 'existing-file')]))),
            new_source('instruction-name',
                       file_name + ' regular'))


class TestCheckForSymLink(TestCaseBase):
    def test_link_fail__when__file_exists_and_is_regular_file(self):
        file_name = 'name-of-existing-file'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file(file_name)]))),
            new_source('instruction-name',
                       file_name + ' symlink'))

    def test_link_fail__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir(file_name)]))),
            new_source('instruction-name',
                       file_name + ' symlink'))

    def test_pass__when__file_type_is_given__link_to_directory(self):
        file_name = 'link-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_dir('dir'),
                      Link(file_name, 'dir')]))),
            new_source('instruction-name',
                       file_name + ' symlink'))

    def test_pass__when__file_type_is_given__link_to_regular_file(self):
        file_name = 'link-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents(
                     [empty_file('file'),
                      Link(file_name, 'file')]))),
            new_source('instruction-name',
                       file_name + ' symlink'))


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.description('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestCheckForRegularFile))
    ret_val.addTest(unittest.makeSuite(TestCheckForDirectory))
    ret_val.addTest(unittest.makeSuite(TestCheckForSymLink))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
