import io
import unittest
from pathlib import Path
from typing import Optional, Sequence, List

import exactly_lib.common.err_msg.definitions
from exactly_lib.common.err_msg.definitions import Block
from exactly_lib.common.report_rendering import source_location as sut
from exactly_lib.common.report_rendering.source_location import SOURCE_LINES_ELEMENT_PROPERTIES, \
    SOURCE_LINES_BLOCK_PROPERTIES
from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.simple_textstruct.file_printer_output import printables as ps
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import LayoutSettings, BlockSettings, \
    PrintablesFactory
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printer, Printable
from exactly_lib.util.simple_textstruct.structure import LineElement, MinorBlock, ElementProperties, MajorBlock
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSourceLines),
        unittest.makeSuite(TestFileInclusionChain),
        unittest.makeSuite(TestSourceLocationPath),
    ])


class TestSourceLines(unittest.TestCase):
    def test(self):
        # ARRANGE #

        single_line = ['the single line']
        multiple_lines = [
            'first',
            'second',
        ]

        cases = [
            NIE('single line',
                expected_source_line_lines(single_line),
                single_line
                ),
            NIE('multiple lines',
                expected_source_line_lines(multiple_lines),
                multiple_lines,
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual_line_element = sut.source_lines_element(case.input_value)
                actual = print_line_element(actual_line_element)

                # ASSERT #

                self.assertEqual(lines_str(case.expected_value),
                                 actual)


class TestFileInclusionChain(unittest.TestCase):
    def test_empty_chain(self):
        # ARRANGE #

        cases = [
            NIE('referrer location is .',
                expected_value=([], Path('.')),
                input_value=Path('.'),
                ),
            NIE('referrer location is dir',
                expected_value=([], Path('a-dir')),
                input_value=Path('a-dir'),
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                line_elements, referrer_location = sut.file_inclusion_chain(case.input_value, [])
                output = print_line_elements(line_elements)
                # ASSERT #

                self.assertEqual(lines_str(case.expected_value[0]), output,
                                 'output')

                self.assertEqual(case.expected_value[1],
                                 referrer_location,
                                 'referrer location')

    def test_non_empty_chain(self):
        # ARRANGE #

        ls1 = single_line_sequence(1, 'line sequence 1')
        ls2 = single_line_sequence(2, 'line sequence 2')

        referrer_location_sub_dir = Path('referrer-location-sub-dir')
        link_sub_dir = Path('link-sub-dir')
        link_sub_dir2 = Path('link-sub-dir-2')
        base_name = Path('base-name')
        base_name2 = Path('base-name-2')

        cases = [
            NIE('single link. referrer location is HERE, file_path_rel_referrer=None',
                expected_value=FileInclusionChainOutput(
                    block=[sut.line_number(ls1.first_line_number)] +
                          expected_source_line_lines(ls1.lines),
                    next_referrer_location=Path('.'),
                ),
                input_value=FileInclusionChainInput(
                    referrer_location=Path('.'),
                    chain=[
                        SourceLocation(
                            source=ls1,
                            file_path_rel_referrer=None
                        )
                    ]
                ),
                ),
            NIE('single link. referrer location is HERE, file_path_rel_referrer just base name',
                expected_value=FileInclusionChainOutput(
                    block=expected_file_reference_lines(base_name, ls1.first_line_number) +
                          expected_source_line_lines(ls1.lines),
                    next_referrer_location=Path('.'),
                ),
                input_value=FileInclusionChainInput(
                    referrer_location=Path('.'),
                    chain=[
                        SourceLocation(
                            source=ls1,
                            file_path_rel_referrer=base_name
                        )
                    ]
                ),
                ),
            NIE('single link. referrer location is HERE, file_path_rel_referrer in sub dir',
                expected_value=FileInclusionChainOutput(
                    block=expected_file_reference_lines(link_sub_dir / base_name, ls1.first_line_number) +
                          expected_source_line_lines(ls1.lines),
                    next_referrer_location=link_sub_dir,
                ),
                input_value=FileInclusionChainInput(
                    referrer_location=Path('.'),
                    chain=[
                        SourceLocation(
                            source=ls1,
                            file_path_rel_referrer=link_sub_dir / base_name
                        )
                    ]
                ),
                ),
            NIE('single link. referrer location is sub-dir, file_path_rel_referrer in sub dir',
                expected_value=FileInclusionChainOutput(
                    block=expected_file_reference_lines(
                        referrer_location_sub_dir / link_sub_dir / base_name,
                        ls1.first_line_number) +
                          expected_source_line_lines(ls1.lines),
                    next_referrer_location=referrer_location_sub_dir / link_sub_dir,
                ),
                input_value=FileInclusionChainInput(
                    referrer_location=referrer_location_sub_dir,
                    chain=[
                        SourceLocation(
                            source=ls1,
                            file_path_rel_referrer=link_sub_dir / base_name
                        )
                    ]
                ),
                ),
            NIE('multiple links. referrer location is sub-dir, file_path_rel_referrer in sub dir',
                expected_value=FileInclusionChainOutput(
                    block=
                    (expected_file_reference_lines(
                        referrer_location_sub_dir / link_sub_dir / base_name,
                        ls1.first_line_number)
                     +
                     expected_source_line_lines(ls1.lines)
                     +
                     expected_file_reference_lines(
                         referrer_location_sub_dir / link_sub_dir / link_sub_dir2 / base_name2,
                         ls2.first_line_number)
                     +
                     expected_source_line_lines(ls2.lines)
                     ),
                    next_referrer_location=referrer_location_sub_dir / link_sub_dir / link_sub_dir2,
                ),
                input_value=FileInclusionChainInput(
                    referrer_location=referrer_location_sub_dir,
                    chain=[
                        SourceLocation(
                            source=ls1,
                            file_path_rel_referrer=link_sub_dir / base_name,
                        ),
                        SourceLocation(
                            source=ls2,
                            file_path_rel_referrer=link_sub_dir2 / base_name2,
                        ),
                    ]
                ),
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                line_elements, referrer_location = sut.file_inclusion_chain(case.input_value.referrer_location,
                                                                            case.input_value.chain)
                output = print_line_elements(line_elements)

                # ASSERT #

                self.assertEqual(lines_str(case.expected_value.block), output,
                                 'output')

                self.assertEqual(case.expected_value.next_referrer_location,
                                 referrer_location,
                                 'referrer location')


class Arrangement:
    def __init__(self,
                 referrer_location: Path,
                 source_location_path: SourceLocationPath
                 ):
        self.referrer_location = referrer_location
        self.source_location_path = source_location_path


class TestSourceLocationPath(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expected: exactly_lib.common.err_msg.definitions.Blocks,
               ):
        actual_blocks = sut.source_location_path(arrangement.referrer_location,
                                                 arrangement.source_location_path)

        actual_output = print_minor_blocks(actual_blocks)
        expected_str = blocks_str(expected)
        self.assertEqual(expected_str, actual_output)

    def test_without_file_inclusion_chain(self):
        # ARRANGE #

        ls = single_line_sequence(1, 'the single line')

        a_dir = Path('a-dir')
        a_file = Path('a-file')

        cases = [
            FilePathCase(
                referrer_location=Path('.'),
                file_path_rel_referrer=None,
                expected_file_path=''
            ),
            FilePathCase(
                referrer_location=a_dir,
                file_path_rel_referrer=None,
                expected_file_path=''
            ),
            FilePathCase(
                referrer_location=Path('.'),
                file_path_rel_referrer=a_file,
                expected_file_path=str(a_file),
            ),
            FilePathCase(
                referrer_location=Path('..'),
                file_path_rel_referrer=a_file,
                expected_file_path=str(Path('..') / a_file),
            ),
            FilePathCase(
                referrer_location=a_dir,
                file_path_rel_referrer=a_file,
                expected_file_path=str(a_dir / a_file),
            ),
            FilePathCase(
                referrer_location=a_dir,
                file_path_rel_referrer=Path('..') / a_file,
                expected_file_path=str(a_file),
            ),
        ]

        for case in cases:
            with self.subTest(case=case):
                slp = SourceLocationPath(SourceLocation(ls, case.file_path_rel_referrer),
                                         [])

                arrangement = Arrangement(case.referrer_location,
                                          slp)

                expected_location_line = (
                    sut.line_number(ls.first_line_number)
                    if case.expected_file_path == ''
                    else
                    case.expected_file_path + ', ' + sut.line_number(ls.first_line_number)
                )

                expected_blocks = [
                    [
                        expected_location_line,
                    ],
                    [
                        LAYOUT.line_element_indent + ls.first_line.text
                    ],
                ]

                # ACT & ASSERT #

                self._check(arrangement,
                            expected_blocks)

    def test_with_file_inclusion_chain(self):
        # ARRANGE #

        final_loc_ls = single_line_sequence(0, 'line sequence 0')
        final_loc_dir = Path('final-loc-dir')
        final_loc_base_name = Path('final-loc-base-name')
        final_location = SourceLocation(final_loc_ls,
                                        final_loc_dir / final_loc_base_name)
        ls1 = single_line_sequence(1, 'line sequence 1')
        ls2 = single_line_sequence(2, 'line sequence 2')

        referrer_location_sub_dir = Path('referrer-location-sub-dir')
        link_sub_dir = Path('link-sub-dir')
        link_sub_dir2 = Path('link-sub-dir-2')
        base_name = Path('base-name')
        base_name2 = Path('base-name-2')

        cases = [
            NIE('single link. referrer location is HERE, file_path_rel_referrer/inclusion=None',
                expected_value=[
                    (
                            [sut.line_number(ls1.first_line_number)]
                            +
                            expected_source_line_lines(ls1.lines)
                            +
                            expected_file_reference_lines(
                                final_loc_dir / final_loc_base_name,
                                final_loc_ls.first_line_number)
                    ),
                    expected_source_line_lines(final_loc_ls.lines)
                ],
                input_value=SourceLocationPathInput(
                    referrer_location=Path('.'),
                    source_location_path=SourceLocationPath(
                        final_location,
                        [
                            SourceLocation(
                                source=ls1,
                                file_path_rel_referrer=None
                            )
                        ])
                ),
                ),
            NIE('multiple links. referrer location is sub-dir, file_path_rel_referrer in sub dir',
                expected_value=[
                    (expected_file_reference_lines(
                        referrer_location_sub_dir / link_sub_dir / base_name,
                        ls1.first_line_number)
                     +
                     expected_source_line_lines(ls1.lines)
                     +
                     expected_file_reference_lines(
                         referrer_location_sub_dir / link_sub_dir / link_sub_dir2 / base_name2,
                         ls2.first_line_number)
                     +
                     expected_source_line_lines(ls2.lines)
                     +
                     expected_file_reference_lines(
                         referrer_location_sub_dir / link_sub_dir / link_sub_dir2 / final_loc_dir / final_loc_base_name,
                         final_loc_ls.first_line_number)
                     ),
                    expected_source_line_lines(final_loc_ls.lines)
                ],
                input_value=SourceLocationPathInput(
                    referrer_location=referrer_location_sub_dir,
                    source_location_path=SourceLocationPath(
                        final_location,
                        [
                            SourceLocation(
                                source=ls1,
                                file_path_rel_referrer=link_sub_dir / base_name,
                            ),
                            SourceLocation(
                                source=ls2,
                                file_path_rel_referrer=link_sub_dir2 / base_name2,
                            ),
                        ])
                ),
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual_blocks = sut.source_location_path(case.input_value.referrer_location,
                                                         case.input_value.source_location_path)

                actual_output = print_minor_blocks(actual_blocks)
                expected_str = blocks_str(case.expected_value)
                # ASSERT #
                self.assertEqual(expected_str, actual_output)


def matches_source_code_minor_block(source_code: Sequence[str]) -> ValueAssertion[MinorBlock]:
    return asrt_struct.matches_minor_block(
        line_elements=asrt.matches_sequence([
            asrt_struct.matches_line_element(
                line_object=asrt_struct.is_string_lines(
                    strings=asrt.equals(source_code),
                ),
                properties=asrt_struct.equals_element_properties(SOURCE_LINES_ELEMENT_PROPERTIES),
            )
        ]),
        properties=asrt_struct.equals_element_properties(SOURCE_LINES_BLOCK_PROPERTIES)
    )


def expected_file_reference_line(file: Path, line_number: int) -> str:
    return str(file) + ', line ' + str(line_number)


def expected_file_reference_lines(file: Path, line_number: int) -> List[str]:
    return [expected_file_reference_line(file, line_number)]


def expected_source_line_lines(lines: Sequence[str]) -> List[str]:
    return [
        LAYOUT.line_element_indent + line
        for line in lines
    ]


def lines_str(x: Sequence[str]) -> str:
    if len(x) == 0:
        return ''
    else:
        return '\n'.join(x) + '\n'


def blocks_str(blocks: Sequence[Sequence[str]]) -> str:
    return MINOR_BLOCKS_SEPARATOR.join([
        lines_str(block)
        for block in blocks
    ])


class FilePathCase:
    def __init__(self,
                 referrer_location: Path,
                 file_path_rel_referrer: Optional[Path],
                 expected_file_path: str):
        self.referrer_location = referrer_location
        self.file_path_rel_referrer = file_path_rel_referrer
        self.expected_file_path = expected_file_path

    def __str__(self):
        return """\
referrer_location={}
file_path_rel_referrer={}
expected_file_path={}""".format(self.referrer_location,
                                self.file_path_rel_referrer,
                                self.expected_file_path)


class FileInclusionChainInput:
    def __init__(self,
                 referrer_location: Path,
                 chain: Sequence[SourceLocation]
                 ):
        self.referrer_location = referrer_location
        self.chain = chain

    def __str__(self):
        return """\
referrer_location={}
chain={}""".format(self.referrer_location,
                   self.chain)


class FileInclusionChainOutput:
    def __init__(self,
                 block: Block,
                 next_referrer_location: Path
                 ):
        self.block = block
        self.next_referrer_location = next_referrer_location


class SourceLocationPathInput:
    def __init__(self,
                 referrer_location: Path,
                 source_location_path: SourceLocationPath,
                 ):
        self.referrer_location = referrer_location
        self.source_location_path = source_location_path

    def __str__(self):
        return """\
referrer_location={}
source_location_path={}""".format(self.referrer_location,
                                  self.source_location_path)


SINGLE_INDENT = ' '
MINOR_BLOCKS_SEPARATOR = '\n'
LAYOUT = LayoutSettings(
    major_block=BlockSettings(SINGLE_INDENT + SINGLE_INDENT + SINGLE_INDENT,
                              ps.SequencePrintable([ps.NEW_LINE_PRINTABLE,
                                                    ps.NEW_LINE_PRINTABLE])
                              ),
    minor_block=BlockSettings(SINGLE_INDENT + SINGLE_INDENT,
                              ps.NEW_LINE_PRINTABLE),
    line_element_indent=SINGLE_INDENT,
)


def print_line_element(line_element: LineElement) -> str:
    printable = PrintablesFactory(LAYOUT).line_element(line_element)
    return print_to_str(printable)


def print_line_elements(line_element: Sequence[LineElement]) -> str:
    block = MinorBlock(line_element, NO_INDENT_NO_COLOR_PROPERTIES)
    printable = PrintablesFactory(LAYOUT).minor_block(block)
    return print_to_str(printable)


def print_minor_blocks(blocks: Sequence[MinorBlock]) -> str:
    block = MajorBlock(blocks, NO_INDENT_NO_COLOR_PROPERTIES)
    printable = PrintablesFactory(LAYOUT).major_block(block)
    return print_to_str(printable)


def print_to_str(printable: Printable) -> str:
    output_file = io.StringIO()
    printer = Printer.new(FilePrinter(output_file))

    printable.print_on(printer)

    return output_file.getvalue()


NO_INDENT_NO_COLOR_PROPERTIES = ElementProperties(False, None)
