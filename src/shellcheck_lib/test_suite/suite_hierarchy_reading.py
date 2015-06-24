import pathlib
import functools

from shellcheck_lib.document.model import PhaseContents
from shellcheck_lib.document.parse import SourceError
from shellcheck_lib.general import line_source
from . import instruction
from . import test_suite_struct
from . import structure
from . import parse
from shellcheck_lib.test_suite.instruction import FileNotAccessibleSimpleError
from shellcheck_lib.test_suite.parse import SuiteFileReferenceError, SuiteSyntaxError, SuiteDoubleInclusion


def read(suite_file_path: pathlib.Path) -> structure.TestSuite:
    """
    :raises SuiteReadError:
    :param suite_file_path:
    :return:
    """
    return _read([], {suite_file_path.resolve()}, suite_file_path)


def _read(inclusions: list,
          visited: set,
          suite_file_path: pathlib.Path) -> structure.TestSuite:
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
    suite_file_path_list, case_file_path_list = _resolve_paths(visited,
                                                               test_suite,
                                                               suite_file_path)
    sub_inclusions = inclusions + [suite_file_path]
    sub_suites_reader = functools.partial(_read, sub_inclusions, visited)
    suite_list = list(map(sub_suites_reader, suite_file_path_list))
    case_list = list(map(structure.TestCase, case_file_path_list))
    return structure.TestSuite(suite_file_path, inclusions, suite_list, case_list)


def _resolve_paths(visited: set,
                   test_suite: test_suite_struct.TestSuite,
                   suite_file_path: pathlib.Path) -> (list, list):
    def paths_for_instructions(env: instruction.Environment,
                               section_contents: PhaseContents,
                               check_visited: bool) -> list:
        ret_val = []
        for element in section_contents.elements:
            if element.is_instruction:
                try:
                    paths = element.instruction.resolve_paths(env)
                    if check_visited:
                        for path in paths:
                            if path in visited:
                                raise SuiteDoubleInclusion(suite_file_path,
                                                           element.source_line,
                                                           path)
                            else:
                                visited.add(path)
                    ret_val.extend(paths)
                except FileNotAccessibleSimpleError as ex:
                    raise SuiteFileReferenceError(suite_file_path,
                                                  element.source_line,
                                                  ex.file_path)
        return ret_val

    environment = instruction.Environment(suite_file_path.parent)
    return (paths_for_instructions(environment, test_suite.suites_section, True),
            paths_for_instructions(environment, test_suite.cases_section, False))
