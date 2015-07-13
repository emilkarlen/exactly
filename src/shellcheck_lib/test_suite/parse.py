import pathlib

from shellcheck_lib.document import model
from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
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


class TestSuiteFileInstruction(instruction.TestSuiteSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_non_wildcard_path(self._file_name, environment)


class TestCaseFileInstruction(instruction.TestCaseSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return _resolve_non_wildcard_path(self._file_name, environment)


def _resolve_non_wildcard_path(file_name: str, environment: instruction.Environment) -> list:
    path = environment.suite_file_dir_path / file_name
    if not path.is_file():
        raise FileNotAccessibleSimpleError(path)
    return [path]


class SuitesSectionParser(parse.InstructionParser):
    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(source_line,
                                             TestSuiteFileInstruction(source_line.text))


class CasesSectionParser(parse.InstructionParser):
    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(source_line,
                                             TestCaseFileInstruction(source_line.text))


PARSER_CONFIGURATION = parse.PhaseAndInstructionsConfiguration(
    None,
    (parse.ParserForPhase(SECTION_NAME__SUITS, SuitesSectionParser()),
     parse.ParserForPhase(SECTION_NAME__CASES, CasesSectionParser()),
     )
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = parse.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_suite_doc.TestSuite:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_suite_doc.TestSuite(
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )


PARSER = Parser()
