import pathlib

from shellcheck_lib.document import parse2
from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.instruction_parser_for_single_phase2 import \
    SectionElementParserForStandardCommentAndEmptyLines
from shellcheck_lib.test_suite import instruction
from shellcheck_lib.test_suite import test_suite_doc
from shellcheck_lib.test_suite.instruction import FileNotAccessibleSimpleError

SECTION_NAME__SUITS = 'suites'
SECTION_NAME__CASES = 'cases'


class SuiteReadError(Exception):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line):
        self._suite_file = suite_file
        self._line = line

    @property
    def suite_file(self) -> pathlib.Path:
        return self._suite_file

    @property
    def line(self) -> line_source.Line:
        return self._line


class SuiteDoubleInclusion(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 included_suite_file: pathlib.Path,
                 first_referenced_from: pathlib.Path):
        super().__init__(suite_file, line)
        self._included_suite_file = included_suite_file
        self._first_referenced_from = first_referenced_from

    @property
    def included_suite_file(self) -> pathlib.Path:
        return self._included_suite_file

    @property
    def first_referenced_from(self) -> pathlib.Path:
        """
        The suite file that contains the first reference to the
        included file.
        :return: None iff the file was mentioned on the command line.
        """
        return self._first_referenced_from


class SuiteFileReferenceError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 reference: pathlib.Path):
        super().__init__(suite_file, line)
        self._reference = reference

    @property
    def reference(self) -> pathlib.Path:
        return self._reference


class SuiteSyntaxError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 message: str):
        super().__init__(suite_file, line)
        self._message = message

    @property
    def message(self) -> str:
        return self._message


class TestSuiteNonWildcardFileInstruction(instruction.TestSuiteSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_non_wildcard_path(self._file_name, environment)


class TestSuiteWildcardFileInstruction(instruction.TestSuiteSectionInstruction):
    """
    Resolves a list of paths from a file-name pattern.
    """

    def __init__(self, pattern: str):
        self._pattern = pattern

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_wildcard_paths(self._pattern, environment)


class TestCaseNonWildcardFileInstruction(instruction.TestCaseSectionInstruction):
    """
    Resolves a single path from a file-name that does not contain wild-cards.
    """

    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_non_wildcard_path(self._file_name, environment)


class TestCaseWildcardFileInstruction(instruction.TestCaseSectionInstruction):
    """
    Resolves a list of paths from a file-name pattern.
    """

    def __init__(self, pattern: str):
        self._pattern = pattern

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_wildcard_paths(self._pattern, environment)


def _resolve_non_wildcard_path(file_name: str, environment: instruction.Environment) -> list:
    path = environment.suite_file_dir_path / file_name
    if not path.is_file():
        raise FileNotAccessibleSimpleError(path)
    return [path]


def _resolve_wildcard_paths(pattern: str, environment: instruction.Environment) -> list:
    paths = sorted(environment.suite_file_dir_path.glob(pattern))
    for path in paths:
        if not path.is_file():
            raise FileNotAccessibleSimpleError(path)
    return paths


class SuitesSectionParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self,
                           source: line_source.LineSequenceBuilder) -> instruction.Instruction:
        line_text = source.first_line.text
        return TestSuiteWildcardFileInstruction(line_text) \
            if _is_wildcard_pattern(line_text) \
            else TestSuiteNonWildcardFileInstruction(line_text)


class CasesSectionParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self,
                           source: line_source.LineSequenceBuilder) -> instruction.Instruction:
        line_text = source.first_line.text
        return TestCaseWildcardFileInstruction(line_text) \
            if _is_wildcard_pattern(line_text) \
            else TestCaseNonWildcardFileInstruction(line_text)


_WILDCARD_CHARACTERS = ('*', '?', '[')


def _contains_any_of(strings_looking_for: tuple, string_looking_in: str):
    for string_looking_for in strings_looking_for:
        if string_looking_in.find(string_looking_for) != -1:
            return True
    return False


def _is_wildcard_pattern(instruction_text: str) -> bool:
    return _contains_any_of(_WILDCARD_CHARACTERS, instruction_text)


PARSER_CONFIGURATION = parse2.SectionsConfiguration(
    None,
    (parse2.SectionConfiguration(SECTION_NAME__SUITS, SuitesSectionParser()),
     parse2.SectionConfiguration(SECTION_NAME__CASES, CasesSectionParser()),
     )
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = parse2.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_suite_doc.TestSuite:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_suite_doc.TestSuite(
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )


PARSER = Parser()
