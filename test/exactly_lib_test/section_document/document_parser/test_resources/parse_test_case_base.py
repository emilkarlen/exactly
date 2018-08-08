import pathlib
import unittest
from typing import Sequence, Dict

from exactly_lib.section_document import model
from exactly_lib.section_document.document_parser import DocumentParser
from exactly_lib_test.section_document.test_resources.document_assertions import matches_document
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

EXPECTED_SOURCE_FILE_PATH = pathlib.Path.cwd()


class ParseTestBase(unittest.TestCase):
    def _parse_lines(self,
                     parser: DocumentParser,
                     lines: Sequence[str]) -> model.Document:
        ptc_source = source_of_lines(lines)
        return parser.parse(EXPECTED_SOURCE_FILE_PATH,
                            ptc_source)

    def _parse_and_check(self,
                         parser: DocumentParser,
                         lines: Sequence[str],
                         expected_document: Dict[str, Sequence[asrt.ValueAssertion[model.SectionContentElement]]]):
        # ACT #
        actual_document = self._parse_lines(parser, lines)
        # ASSERT #
        assertion = matches_document(expected_document)
        assertion.apply_without_message(self, actual_document)
