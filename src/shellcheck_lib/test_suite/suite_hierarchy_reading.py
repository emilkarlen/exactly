import pathlib

from shellcheck_lib.document.model import PhaseContents
from shellcheck_lib.document.parse import SourceError
from shellcheck_lib.general import line_source
from . import instruction
from . import test_suite_struct
from . import structure
from . import parse
from shellcheck_lib.test_suite.instruction import FileNotAccessibleSimpleError
from shellcheck_lib.test_suite.parse import SuiteFileReferenceError, SuiteSyntaxError


def read(suite_file_path: pathlib.Path) -> structure.TestSuite:
    """
    :raises SuiteReadError:
    :param suite_file_path:
    :return:
    """
    source = line_source.new_for_file(suite_file_path)
    try:
        test_suite = parse.PARSER.apply(source)
    except SourceError as ex:
        raise SuiteSyntaxError(suite_file_path,
                               ex.line,
                               ex.message)
    suite_file_path_list, case_file_path_list = _resolve_paths(test_suite,
                                                               suite_file_path)
    suite_list = list(map(read, suite_file_path_list))
    case_list = list(map(structure.TestCase, case_file_path_list))
    return structure.TestSuite(suite_list, case_list)


def _resolve_paths(test_suite: test_suite_struct.TestSuite,
                   suite_file_path: pathlib.Path) -> (list, list):
    def paths_for_instructions(env: instruction.Environment,
                               section_contents: PhaseContents) -> list:
        ret_val = []
        for element in section_contents.elements:
            if element.is_instruction:
                try:
                    ret_val.extend(element.instruction.resolve_paths(env))
                except FileNotAccessibleSimpleError as ex:
                    raise SuiteFileReferenceError(suite_file_path,
                                                  element.source_line,
                                                  ex.file_path)
        return ret_val

    environment = instruction.Environment(suite_file_path.parent)
    return (paths_for_instructions(environment, test_suite.suites_section),
            paths_for_instructions(environment, test_suite.cases_section))
