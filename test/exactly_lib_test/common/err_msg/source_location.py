import unittest
from pathlib import Path
from typing import Optional, Sequence, List

import exactly_lib.common.err_msg.definitions
from exactly_lib.common.err_msg import source_location as sut
from exactly_lib.common.err_msg.definitions import Block
from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.test_resources.test_utils import NIE


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

        formatter = sut.default_formatter()

        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = formatter.source_lines(case.input_value)

                # ASSERT #

                self.assertEqual(case.expected_value,
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

        formatter = sut.default_formatter()

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                block, referrer_location = formatter.file_inclusion_chain(case.input_value,
                                                                          [])

                # ASSERT #

                self.assertEqual(case.expected_value[0], block,
                                 'block')

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
                    block=expected_path_lines(base_name, ls1.first_line_number) +
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
                    block=expected_path_lines(link_sub_dir / base_name, ls1.first_line_number) +
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
                    block=expected_path_lines(
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
                    (expected_path_lines(
                        referrer_location_sub_dir / link_sub_dir / base_name,
                        ls1.first_line_number)
                     +
                     expected_source_line_lines(ls1.lines)
                     +
                     expected_path_lines(
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

        formatter = sut.default_formatter()

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                block, referrer_location = formatter.file_inclusion_chain(case.input_value.referrer_location,
                                                                          case.input_value.chain)

                # ASSERT #

                self.assertEqual(case.expected_value.block, block,
                                 'block')

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
        formatter = sut.default_formatter()
        actual = formatter.source_location_path(arrangement.referrer_location,
                                                arrangement.source_location_path)
        self.assertEqual(expected, actual)

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
                        sut.SOURCE_LINE_INDENT + ls.first_line.text
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
                            expected_path_lines(
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
                    (expected_path_lines(
                        referrer_location_sub_dir / link_sub_dir / base_name,
                        ls1.first_line_number)
                     +
                     expected_source_line_lines(ls1.lines)
                     +
                     expected_path_lines(
                         referrer_location_sub_dir / link_sub_dir / link_sub_dir2 / base_name2,
                         ls2.first_line_number)
                     +
                     expected_source_line_lines(ls2.lines)
                     +
                     expected_path_lines(
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

        formatter = sut.default_formatter()

        for case in cases:
            with self.subTest(case.name):
                # ACT #
                blocks = formatter.source_location_path(case.input_value.referrer_location,
                                                        case.input_value.source_location_path)

                # ASSERT #

                self.assertEqual(case.expected_value, blocks)


def expected_path_lines(file: Path, line_number: int) -> List[str]:
    return [str(file) + ', line ' + str(line_number)]


def expected_source_line_lines(lines: Sequence[str]) -> List[str]:
    return [
        sut.SOURCE_LINE_INDENT + line
        for line in lines
    ]


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
