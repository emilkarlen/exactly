import pathlib
import unittest

from exactly_lib.common.report_rendering.parts import source_location
from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.simple_textstruct.structure import MinorBlock
from exactly_lib_test.common.report_rendering.source_location import matches_source_code_minor_block, \
    expected_path_line
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestOutputLocation)


class TestOutputLocation(unittest.TestCase):
    def test_no_source_and_no_description(self):
        # ARRANGE #
        section_name = 'section-name'
        cases = [
            NIE(
                'with no section',
                expected_value=asrt.is_empty_sequence,
                input_value=None,
            ),
            NIE(
                'with section',
                expected_value=asrt.matches_sequence([
                    _matches_plain_minor_block_w_single_plain_line(section_line(section_name))
                ]),
                input_value=section_name
            ),
        ]
        for case in cases:
            with self.subTest(case.name,
                              blocks_renderer='minor blocks'):
                # ACT #
                actual_renderer = source_location.location_minor_blocks_renderer(
                    None,
                    case.input_value,
                    None)
                actual = actual_renderer.render_sequence()
                # ASSERT #
                case.expected_value.apply_without_message(self,
                                                          actual)

            with self.subTest(case.name,
                              blocks_renderer='major blocks'):
                # ACT #
                actual_renderer = source_location.location_blocks_renderer(
                    None,
                    case.input_value,
                    None)
                actual = actual_renderer.render_sequence()
                # ASSERT #
                expected = asrt.matches_sequence([
                    asrt_struct.matches_major_block__w_plain_properties(
                        minor_blocks=case.expected_value,
                    )
                ])
                expected.apply_without_message(self,
                                               actual)

    def test_with_source(self):
        # ARRANGE #
        section_name = 'section-name'
        line_sequence_a = LineSequence(2, ['source a 1',
                                           'source a 2'])
        file_path_a = pathlib.Path('file-a.src')

        minor_blocks_expectation = asrt.matches_sequence(
            [
                _matches_plain_minor_block_w_single_plain_line(section_line(section_name)),
                _matches_plain_minor_block_w_single_plain_line(file_and_line_num_line(file_path_a,
                                                                                      line_sequence_a)),
                matches_source_code_minor_block(line_sequence_a.lines),
            ]
        )
        input_value = SourceLocationPath(
            location=SourceLocation(line_sequence_a,
                                    file_path_a),
            file_inclusion_chain=[]
        )

        with self.subTest(blocks_rendering='minor blocks'):
            # ACT #
            actual_renderer = source_location.location_minor_blocks_renderer(
                input_value,
                section_name,
                None)
            actual = actual_renderer.render_sequence()
            # ASSERT #
            minor_blocks_expectation.apply_without_message(self,
                                                           actual)

        with self.subTest(blocks_rendering='major blocks'):
            expected_major_blocks = asrt.matches_sequence([
                asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=minor_blocks_expectation
                )

            ])
            # ACT #
            actual_renderer = source_location.location_blocks_renderer(
                input_value,
                section_name,
                None)
            actual = actual_renderer.render_sequence()
            # ASSERT #
            expected_major_blocks.apply_without_message(self,
                                                        actual)


def section_line(section_name: str) -> str:
    return 'In ' + section_header(section_name)


def file_and_line_num_line(file_path: pathlib.Path,
                           source: LineSequence) -> str:
    return expected_path_line(file_path,
                              source.first_line_number)


def _matches_plain_minor_block_w_single_plain_line(line: str) -> ValueAssertion[MinorBlock]:
    return asrt_struct.matches_minor_block__w_plain_properties(
        asrt.matches_sequence([
            asrt_struct.matches_line_element__w_plain_properties(
                asrt_struct.is_string__not_line_ended(asrt.equals(line))
            ),
        ])
    )
