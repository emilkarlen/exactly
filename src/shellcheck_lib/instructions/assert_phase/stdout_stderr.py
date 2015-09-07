import shlex

from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction
from .utils import contents_utils

syntax_list = [
    ('stdout empty', 'File exists, is a regular file, and is empty'),
    ('stdout ! empty', 'File exists, is a regular file, and is not empty'),
    ('stdout contents --rel-home FILE',
     'Compares contents of FILENAME to contents of FILE (which is a path relative home)'),
    ('stdout contents --rel-cwd FILE',
     'Compares contents of FILENAME to contents of FILE (which is a path relative current working directory)'),
]


class ParserForContentsForTarget(SingleInstructionParser):
    def __init__(self,
                 comparison_target: contents_utils.ComparisonTarget):
        self.comparison_target = comparison_target

    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> AssertPhaseInstruction:
        arguments = shlex.split(instruction_argument)
        content_instruction = contents_utils.try_parse_content(self.comparison_target, arguments)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(str(arguments))
        return content_instruction


class ParserForContentsForStdout(ParserForContentsForTarget):
    def __init__(self):
        super().__init__(contents_utils.StdoutComparisonTarget())


class ParserForContentsForStderr(ParserForContentsForTarget):
    def __init__(self):
        super().__init__(contents_utils.StderrComparisonTarget())
