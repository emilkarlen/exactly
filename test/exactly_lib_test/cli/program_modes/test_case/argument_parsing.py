import unittest
from typing import List

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options
from exactly_lib.cli.program_modes.test_case import argument_parsing as sut
from exactly_lib.util.argument_parsing_utils import ArgumentParsingError
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.processing.test_resources.test_case_setup import test_case_handling_setup
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


class TestCase(unittest.TestCase):
    TEST_CASE_HANDLING_SETUP = test_case_handling_setup()

    def test_resolve_hds_directory(self):
        # ARRANGE #
        with tmp_file_containing('') as file_path:
            argv = [str(file_path)]
            expected_hds_path = file_path.parent.resolve()
            # ACT #
            result = sut.parse(test_case_handling_setup(),
                               sandbox_root_name_resolver.for_test(),
                               argv, {})
        # ASSERT #
        self.assertEqual(expected_hds_path,
                         result.initial_hds_dir_path,
                         'Initial Home Directory')

    def test_fail_WHEN_actor_argument_is_invalidly_quoted(self):
        empty_case_file = fs.File.empty('test.case')
        self._expect_raise_argument_parsing_error(
            cwd_contents=DirContents([empty_case_file]),
            arguments=[common_cli_options.OPTION_FOR_ACTOR,
                       "word 'unmatched quote in actor argument",
                       empty_case_file.name]
        )

    def test_fail_WHEN_actor_argument_is_empty(self):
        empty_case_file = fs.File.empty('test.case')
        self._expect_raise_argument_parsing_error(
            cwd_contents=DirContents([empty_case_file]),
            arguments=[common_cli_options.OPTION_FOR_ACTOR,
                       '',
                       empty_case_file.name]
        )

    def test_fail_WHEN_preprocessor_argument_is_invalidly_quoted(self):
        empty_case_file = fs.File.empty('test.case')
        self._expect_raise_argument_parsing_error(
            cwd_contents=DirContents([empty_case_file]),
            arguments=[command_line_options.OPTION_FOR_PREPROCESSOR,
                       "word 'unmatched quote in preprocessor argument",
                       empty_case_file.name]
        )

    def test_fail_WHEN_preprocessor_argument_is_empty(self):
        empty_case_file = fs.File.empty('test.case')
        self._expect_raise_argument_parsing_error(
            cwd_contents=DirContents([empty_case_file]),
            arguments=[command_line_options.OPTION_FOR_PREPROCESSOR,
                       '',
                       empty_case_file.name]
        )

    def _expect_raise_argument_parsing_error(self,
                                             cwd_contents: DirContents,
                                             arguments: List[str]):
        with tmp_dir_as_cwd(cwd_contents):
            with self.assertRaises(ArgumentParsingError):
                sut.parse(self.TEST_CASE_HANDLING_SETUP,
                          sandbox_root_name_resolver.for_test(),
                          arguments,
                          {})


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
