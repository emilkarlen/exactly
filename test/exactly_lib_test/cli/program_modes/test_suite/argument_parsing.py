import unittest
from pathlib import Path
from typing import List

from exactly_lib.cli.program_modes.test_suite import argument_parsing as sut
from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.util.argument_parsing_utils import ArgumentParsingError
from exactly_lib_test.processing.test_resources.test_case_setup import setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, Dir, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSuiteFile)


class TestSuiteFile(unittest.TestCase):
    handling_setup = setup_with_null_act_phase_and_null_preprocessing()

    def test_fail_WHEN_no_file_argument(self):
        self._expect_raise_argument_parsing_error(
            cwd_contents=empty_dir_contents(),
            arguments=[]
        )

    def test_fail_WHEN_file_argument_do_not_exit(self):
        self._expect_raise_argument_parsing_error(
            cwd_contents=empty_dir_contents(),
            arguments=['non-existing.suite']
        )

    def test_succeed_WHEN_file_argument_do_exit(self):
        existing_file = File.empty('existing-file.ext')
        self._expect_successful_parse(
            cwd_contents=DirContents([existing_file]),
            arguments=[existing_file.name],
            expected_file_path=existing_file.name_as_path,
        )

    def test_pass_WHEN_file_argument_do_exit_as_dir_and_dir_contains_default_suite_file(self):
        dir_with_default_suite_file = Dir('a-dir', [
            File.empty(file_names.DEFAULT_SUITE_FILE)
        ])
        self._expect_successful_parse(
            cwd_contents=DirContents([dir_with_default_suite_file]),
            arguments=[dir_with_default_suite_file.name],
            expected_file_path=dir_with_default_suite_file.name_as_path / file_names.DEFAULT_SUITE_FILE,
        )

    def test_fail_WHEN_file_argument_do_exit_as_dir_but_do_not_contain_default_suite_file(self):
        existing_dir = Dir.empty('existing-dir')
        self._expect_raise_argument_parsing_error(
            cwd_contents=DirContents([existing_dir]),
            arguments=[existing_dir.name]
        )

    def _expect_raise_argument_parsing_error(self,
                                             cwd_contents: DirContents,
                                             arguments: List[str]):
        with tmp_dir_as_cwd(cwd_contents):
            with self.assertRaises(ArgumentParsingError):
                return sut.parse(self.handling_setup, arguments)

    def _expect_successful_parse(self,
                                 cwd_contents: DirContents,
                                 arguments: List[str],
                                 expected_file_path: Path):
        with tmp_dir_as_cwd(cwd_contents):
            actual_settings = sut.parse(self.handling_setup, arguments)
        self.assertEqual(expected_file_path,
                         actual_settings.suite_root_file_path)

    def _do_parse(self, arguments: List[str]) -> TestSuiteExecutionSettings:
        return sut.parse(self.handling_setup, arguments)
