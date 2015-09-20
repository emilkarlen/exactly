from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SectionElementParserForStandardCommentAndEmptyLines
from shellcheck_lib.test_suite.instruction_set import instruction, utils


class SuitesSectionParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self,
                           source: line_source.LineSequenceBuilder) -> instruction.Instruction:
        line_text = source.first_line.text
        return TestSuiteWildcardFileInstruction(line_text) \
            if utils.is_wildcard_pattern(line_text) \
            else TestSuiteNonWildcardFileInstruction(line_text)


class TestSuiteNonWildcardFileInstruction(instruction.TestSuiteSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_non_wildcard_path(self._file_name, environment)


class TestSuiteWildcardFileInstruction(instruction.TestSuiteSectionInstruction):
    """
    Resolves a list of paths from a file-name pattern.
    """

    def __init__(self, pattern: str):
        self._pattern = pattern

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_wildcard_paths(self._pattern, environment)
