import functools
import itertools
import unittest
from typing import Sequence, List, Tuple

from exactly_lib.impls.actors.util import source_code_lines as sut
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestNoLines(),
        TestOneOrMoreLines(),
    ])


class TestNoLines(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue(
                'no instructions',
                (),
            ),
            NameAndValue(
                'single instruction',
                (instr([]),),
            ),
            NameAndValue(
                'two instructions',
                (instr([]), instr([])),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual__as_lines = sut.all_source_code_lines__std_syntax(case.value)
                actual__as_str = sut.all_source_code_lines_str__std_syntax(case.value)

                # ASSERT #

                self.assertEqual(
                    actual__as_lines,
                    [],
                    'as lines'
                )

                self.assertEqual(
                    actual__as_str,
                    '',
                    'as str'
                )


class TestOneOrMoreLines(unittest.TestCase):
    def runTest(self):
        for lines_combination in LINES_COMBINATIONS:
            for instructions_setup in InstructionsSetup.of_one_or_two_instruction_from_perms_of(lines_combination):
                with self.subTest(lines_combination=list(map(str, lines_combination)),
                                  the_instructions_variant=instructions_setup.instructions_as_lists):
                    # ACT #
                    actual__as_lines = sut.all_source_code_lines__std_syntax(instructions_setup.instructions)
                    actual__as_str = sut.all_source_code_lines_str__std_syntax(instructions_setup.instructions)

                    # ASSERT #

                    self.assertEqual(
                        actual__as_lines,
                        instructions_setup.expected,
                        'as lines'
                    )

                    self.assertEqual(
                        actual__as_str,
                        expected_str_from_lines(instructions_setup.expected),
                        'as str'
                    )


class LineSetup:
    def __init__(self,
                 line: str,
                 expected: List[str],
                 ):
        self.line = line
        self.expected = expected

    def __str__(self):
        return self.line

    @staticmethod
    def of_source(line: str) -> 'LineSetup':
        return LineSetup(line, [line])

    @staticmethod
    def of_non_source(line: str) -> 'LineSetup':
        return LineSetup(line, [])


class LinesSetup:
    def __init__(self,
                 lines: List[str],
                 expected: List[str],
                 ):
        self.lines = lines
        self.expected = expected

    @staticmethod
    def empty() -> 'LinesSetup':
        return LinesSetup([], [])

    def add(self, line: LineSetup) -> 'LinesSetup':
        return LinesSetup(
            self.lines + [line.line],
            self.expected + line.expected
        )

    @staticmethod
    def of(lines: Tuple[LineSetup, ...]) -> 'LinesSetup':
        return functools.reduce(LinesSetup.add, lines, LinesSetup.empty())

    @staticmethod
    def setups_from_lines(lines: List[LineSetup]) -> List['LinesSetup']:
        return [
            LinesSetup.of(permutation)
            for permutation in perms(lines)
        ]


class InstructionsSetup:
    def __init__(self,
                 instructions: List[ActPhaseInstruction],
                 instructions_as_lists: List[List[str]],
                 expected: List[str],
                 ):
        self.instructions = instructions
        self.instructions_as_lists = list(map(tuple, instructions_as_lists))
        self.expected = expected

    @staticmethod
    def of_one_instruction(lines: LinesSetup) -> 'InstructionsSetup':
        return InstructionsSetup([instr(lines.lines)],
                                 [lines.lines],
                                 lines.expected)

    @staticmethod
    def of_two_instruction(lines: LinesSetup) -> List['InstructionsSetup']:
        n = len(lines.lines)
        return [
            InstructionsSetup(
                [
                    instr(lines.lines[:i]),
                    instr(lines.lines[i:]),
                ],
                [
                    lines.lines[:i],
                    lines.lines[i:],
                ],
                lines.expected,
            )
            for i in range(n + 1)
        ]

    @staticmethod
    def of_one_or_two_instruction(lines: LinesSetup) -> List['InstructionsSetup']:
        return ([InstructionsSetup.of_one_instruction(lines)] +
                InstructionsSetup.of_two_instruction(lines)
                )

    @staticmethod
    def of_one_or_two_instruction_from_perms_of(lines: List[LineSetup]) -> List['InstructionsSetup']:
        lines_setups = LinesSetup.setups_from_lines(lines)
        return list(itertools.chain.from_iterable([
            InstructionsSetup.of_one_or_two_instruction(lines_setup)
            for lines_setup in lines_setups
        ]))


def perms(lines: List[LineSetup]) -> List[Tuple[LineSetup, ...]]:
    return list(itertools.permutations(lines))


SOURCE_1 = LineSetup.of_source(' source line 1')
SOURCE_2 = LineSetup.of_source('source line 2  ')
COMMENT = LineSetup.of_non_source('  ' + LINE_COMMENT_MARKER + ' comment')
EMPTY = LineSetup.of_non_source('  ')

LINES_COMBINATIONS = [
    [SOURCE_1],
    [COMMENT],
    [EMPTY],
    [SOURCE_1, SOURCE_2],
    [SOURCE_1, COMMENT],
    [COMMENT, EMPTY],
    [SOURCE_1, COMMENT, EMPTY],
    [SOURCE_1, SOURCE_2, COMMENT, EMPTY],
]


def expected_str_from_lines(lines: Sequence[str]) -> str:
    nl_sep = '\n'.join(lines)
    return (
        ''
        if len(nl_sep) == 0
        else
        nl_sep + '\n'
    )
