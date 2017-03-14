import unittest

from exactly_lib.instructions.assert_ import type as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import TestCaseBase, \
    arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Link


class TestParse(TestCaseBase):
    def test_raise_exception_when_syntax_is_invalid(self):
        test_cases = [
            '',
            'file-name file extra-argument',
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


class TestCheckForDirectory(TestCaseBaseForParser):
    def test_pass__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_DIRECTORY,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir(file_name)]))),
            is_pass(),
        )

    def test_fail__when__actual_type_is_regular_file(self):
        file_name = 'name-of-existing-directory'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_DIRECTORY,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__actual_type_is_sym_link_to_directory(self):
        file_name = 'sym-link'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_DIRECTORY,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('directory'),
                 Link(file_name, 'directory')]))),
            is_pass(),
        )

    def test_fail__when__actual_type_is_sym_link_to_file(self):
        file_name = 'sym-link'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_DIRECTORY,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file('existing-file'),
                 Link(file_name, 'existing-file')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestCheckForRegularFile(TestCaseBaseForParser):
    def test_pass__when__actual_type_is_regular_file(self):
        file_name = 'name-of-existing-directory'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_REGULAR,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file(file_name)]))),
            is_pass(),
        )

    def test_fail__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_REGULAR,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__actual_type_is_sym_link_to_directory(self):
        file_name = 'sym-link'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_REGULAR,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('directory'),
                 Link(file_name, 'directory')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__actual_type_is_sym_link_to_file(self):
        file_name = 'sym-link'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_REGULAR,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file('existing-file'),
                 Link(file_name, 'existing-file')]))),
            is_pass(),
        )


class TestCheckForSymLink(TestCaseBaseForParser):
    def test_link_fail__when__file_exists_and_is_regular_file(self):
        file_name = 'name-of-existing-file'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_SYMLINK,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_link_fail__when__file_type_is_given__directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_SYMLINK,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir(file_name)]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__file_type_is_given__link_to_directory(self):
        file_name = 'link-file'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_SYMLINK,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('dir'),
                 Link(file_name, 'dir')]))),
            is_pass(),
        )

    def test_pass__when__file_type_is_given__link_to_regular_file(self):
        file_name = 'link-file'
        self._run(
            file_name + ' ' + sut.TYPE_NAME_SYMLINK,
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_file('file'),
                 Link(file_name, 'file')]))),
            is_pass(),
        )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestCheckForRegularFile),
        unittest.makeSuite(TestCheckForDirectory),
        unittest.makeSuite(TestCheckForSymLink),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
