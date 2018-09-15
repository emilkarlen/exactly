import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import List

from exactly_lib.section_document import parsed_section_element
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_suite.instruction_set.instruction import FileNotAccessibleSimpleError, \
    TestSuiteFileReferencesInstruction
from exactly_lib.test_suite.instruction_set.sections import suites as sut
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir


class ResolvePathsTestBase(unittest.TestCase):

    def _expected_instruction_class(self):
        raise NotImplementedError()

    def _parser(self) -> SectionElementParser:
        raise NotImplementedError()

    def _expect_success(self,
                        contents_dir_contents: DirContents,
                        source: str,
                        expected_contents_rel_contents_dir: List[Path],
                        ):
        with self._setup(contents_dir_contents, source) as (instruction, contents_dir):
            environment = sut.Environment(contents_dir)
            actual = instruction.resolve_paths(environment)
            # ASSERT #
            expected_paths = [
                contents_dir / expected_path
                for expected_path in expected_contents_rel_contents_dir
            ]
            self.assertEqual(expected_paths,
                             actual,
                             'resolved paths')

    def _expect_resolving_error(self,
                                contents_dir_contents: DirContents,
                                source: str,
                                ):
        with self._setup(contents_dir_contents, source) as (instruction, contents_dir):
            environment = sut.Environment(contents_dir)
            # ACT & ASSERT #
            with self.assertRaises(FileNotAccessibleSimpleError):
                instruction.resolve_paths(environment)

    @contextmanager
    def _setup(self,
               contents_dir_contents: DirContents,
               source: str,
               ):
        # ARRANGE #
        parse_source = remaining_source(source)
        # ACT #
        actual_parse_result = self._parser().parse(ARBITRARY_FS_LOCATION_INFO,
                                                   parse_source)
        # ASSERT preconditions #

        self.assertIsInstance(actual_parse_result,
                              parsed_section_element.ParsedInstruction)
        instruction = actual_parse_result.instruction_info.instruction
        self.assertIsInstance(instruction,
                              self._expected_instruction_class())
        assert isinstance(instruction, TestSuiteFileReferencesInstruction)

        with tmp_dir(contents_dir_contents) as contents_dir:
            yield instruction, contents_dir
