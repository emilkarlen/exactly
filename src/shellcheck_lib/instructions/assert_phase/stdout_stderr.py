import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from .utils import contents_utils


def description(file: str) -> Description:
    return Description(
        'Test the contents of %s' % file,
        '',
        [
            InvokationVariant(
                'empty',
                '%s is empty' % file),
            InvokationVariant(
                '! empty',
                '%s is not empty' % file),
            InvokationVariant(
                '--rel-home FILE',
                """Expects the contents of %s to equal the contents of FILE
                (which is a path relative home)""" % file),
            InvokationVariant(
                '--rel-cwd FILE',
                """Expects the contents of %s to equal the contents of FILE
                (which is a path relative current working directory)""" % file),
        ])


class ParserForContentsForTarget(SingleInstructionParser):
    def __init__(self,
                 comparison_target: contents_utils.ComparisonTarget):
        self.comparison_target = comparison_target

    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
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
