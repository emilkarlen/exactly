import unittest
from pathlib import Path

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document.document_parser import SectionsConfiguration
from exactly_lib.section_document.model import Document
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import SECTIONS_CONFIGURATION
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement:
    def __init__(self,
                 sections_configuration: SectionsConfiguration,
                 cwd_dir_contents: DirContents,
                 root_file: Path):
        self.sections_configuration = sections_configuration
        self.cwd_dir_contents = cwd_dir_contents
        self.root_file = root_file


def std_conf_arrangement(cwd_dir_contents: DirContents,
                         root_file: Path) -> Arrangement:
    return Arrangement(SECTIONS_CONFIGURATION, cwd_dir_contents, root_file)


class Expectation:
    def __init__(self, document: asrt.ValueAssertion[Document]):
        self.document = document


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    # ARRANGE #
    with tmp_dir_as_cwd(arrangement.cwd_dir_contents):
        # ACT #
        actual = sut.parse(arrangement.sections_configuration, arrangement.root_file)
        # ASSERT #
        expectation.document.apply_without_message(put, actual)


def check_and_expect_exception(put: unittest.TestCase,
                               arrangement: Arrangement,
                               expected_exception: asrt.ValueAssertion[Exception]):
    with tmp_dir_as_cwd(arrangement.cwd_dir_contents):
        with put.assertRaises(Exception) as cm:
            # ACT & ASSERT #
            sut.parse(arrangement.sections_configuration, arrangement.root_file)
        expected_exception.apply_with_message(put, cm.exception, 'Exception')
