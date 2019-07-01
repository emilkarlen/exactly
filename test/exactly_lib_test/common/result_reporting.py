import io
import os
import pathlib
import unittest
from typing import List

from exactly_lib.common import result_reporting as sut
from exactly_lib.common.err_msg.definitions import SOURCE_LINE_INDENT
from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestOutputLocation)


class TestOutputLocation(unittest.TestCase):
    def test_no_source_and_no_description(self):
        # ARRANGE #
        section_name = 'section-name'
        cases = [
            NIE(
                'with no section',
                expected_value=lines_string([]),
                input_value=None,
            ),
            NIE(
                'with section',
                expected_value=lines_string([
                    section_line(section_name),
                    '',
                ]),
                input_value=section_name
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                output_file = io.StringIO()
                # ACT #
                sut.output_location(FilePrinter(output_file),
                                    None,
                                    case.input_value,
                                    None)
                # ASSERT #
                actual = output_file.getvalue()
                output_file.close()
                self.assertEqual(case.expected_value,
                                 actual)

    def test_with_source(self):
        # ARRANGE #
        section_name = 'section-name'
        line_sequence_a = LineSequence(2, ['source a 1',
                                           'source a 2'])
        file_path_a = pathlib.Path('file-a.src')

        expected_value = lines_string(
            [
                section_line(section_name),
                file_and_line_num_line(file_path_a, line_sequence_a),
                '',
            ] +
            source_lines(line_sequence_a) +
            [
                ''
            ]
        )
        input_value = SourceLocationPath(
            location=SourceLocation(line_sequence_a,
                                    file_path_a),
            file_inclusion_chain=[]
        )

        output_file = io.StringIO()
        # ACT #
        sut.output_location(FilePrinter(output_file),
                            input_value,
                            section_name,
                            None)
        # ASSERT #
        actual = output_file.getvalue()
        output_file.close()
        self.assertEqual(expected_value,
                         actual)


def file_inclusion_chain_location(location: SourceLocation) -> List[str]:
    return (
            [
                str(location.file_path_rel_referrer) + ', line ' + str(location.source.first_line_number),
            ] +
            [
                '  ' + line_text
                for line_text in location.source.lines
            ] +
            [
                ''
            ]
    )


def source_lines(line_sequence: LineSequence) -> List[str]:
    return [SOURCE_LINE_INDENT + line
            for line in line_sequence.lines]


def section_line(section_name: str) -> str:
    return 'In ' + section_header(section_name)


def file_line(file_path: pathlib.Path) -> str:
    return str(file_path)


def file_and_line_num_line(file_path: pathlib.Path,
                           source: LineSequence) -> str:
    return str(file_path) + ', line ' + str(source.first_line_number)


def lines_string(lines: List[str]) -> str:
    return ''.join([line + os.linesep
                    for line in lines])
