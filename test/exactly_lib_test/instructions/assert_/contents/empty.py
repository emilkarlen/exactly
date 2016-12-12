import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.contents.test_resources import TestCaseBaseForParser
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, \
    Expectation, is_pass
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2


class TestFileContentsEmptyInvalidSyntax(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name empty superfluous-argument'
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(arguments))


class TestFileContentsEmptyValidSyntax(TestCaseBaseForParser):
    def test_fail__when__file_do_not_exist(self):
        self._run(
            new_source2('name-of-non-existing-file empty'),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail())
        )

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
            new_source2(file_name + ' empty'),
            arrangement(sds_contents_before_main=act_dir_contents(
                DirContents([empty_dir(file_name)]))),
            Expectation(main_result=pfh_check.is_fail())
        )

    def test_fail__when__file_exists_but_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
            new_source2(file_name + ' empty'),
            arrangement(sds_contents_before_main=act_dir_contents(
                DirContents([File(file_name, 'contents')]))),
            Expectation(main_result=pfh_check.is_fail())
        )

    def test_pass__when__file_exists_and_is_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
            new_source2(file_name + ' empty'),
            arrangement(sds_contents_before_main=act_dir_contents(
                DirContents([empty_file(file_name)]))),
            is_pass()
        )


class TestFileContentsNonEmptyInvalidSyntax(TestCaseBaseForParser):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name ! empty superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._run(
                new_source2(arguments),
                arrangement(),
                is_pass(),
            )


class TestFileContentsNonEmptyValidSyntax(TestCaseBaseForParser):
    def test_fail__when__file_do_not_exist(self):
        self._run(
            new_source2('name-of-non-existing-file ! empty'),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
            new_source2(file_name + ' ! empty'),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__file_exists_but_is_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
            new_source2(file_name + ' ! empty'),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__file_exists_and_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
            new_source2(file_name + ' ! empty'),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [File(file_name, 'contents')]))),
            is_pass(),
        )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileContentsEmptyInvalidSyntax),
        unittest.makeSuite(TestFileContentsEmptyValidSyntax),
        unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntax),
        unittest.makeSuite(TestFileContentsNonEmptyValidSyntax),
    ])
